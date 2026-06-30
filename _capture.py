#!/usr/bin/env python3

import logging
import cv2 as cv
from typing import ( Self, 
                     List,
                     Set,
                    )
import numpy as np
import time
import argparse

from pymavlink import mavutil
from pynput import keyboard
import threading
import queue


logging.basicConfig(
        level = logging.INFO,
        format = " %(asctime)s [%(levelname)s] %(filename)s : %(lineno)d - %(message)s",
        datefmt = "%H:%M:%S" 
    )

logging.getLogger("ultralytics").setLevel(logging.ERROR)


parser = argparse.ArgumentParser()

# for whether it is in controller mode or not
parser.add_argument("--controller",
                    type = bool,
                    default = False,
                    help = "check for the controller mode"
                    )

# RC channel without controller

"""
Get PWM Values for the Drone RC Control
roll-left or right
pitch-forward or backward
throttle- accelaration
yaw- angular motion
"""

parser.add_argument("--roll",
                    type = int,
                    default = 1500,
                    help = "Roll default PWM value -> 1500"
                    )
parser.add_argument("--pitch",
                    type = int,
                    default = 1500,
                    help = "Pitch default PWM value -> 1500"
                    )
parser.add_argument("--throttle", 
                    type = int,
                    default = 1500,
                    help = "Throttle default PWM value -> 1500"
                    )
parser.add_argument("--yaw", 
                    type = int,
                    default = 1500,
                    help = "Yaw default PWM value -> 1500"
                    )
args = parser.parse_args()

# import and load YOLO model
try:
    from ultralytics import YOLO
    model = YOLO("yolov8n.pt")
    YOLO_AVAILABLE = True
except:
    print("YOLO Not available")
    YOLO_AVAILABLE = False


class Sitl:
    def __init__(self : Self,
                 roll : int,
                 pitch : int,
                 throttle : int,
                 yaw : int
        ) -> None:
        self.roll = roll
        self.pitch = pitch 
        self.throttle = throttle
        self.yaw = yaw  

    def create_connection(self : Self) -> None:
        connection_string : str = "udp:127.0.0.1:14552"
        print(f"Connecting to sitl on {connection_string}")
        try:
            global master 
            master = mavutil.mavlink_connection(connection_string)
            
            print("Waiting for heart Beat")
            heartbeat = master.wait_heartbeat(timeout = 5)

            if heartbeat is None:
                logging.error("there is no Heartbeat comes from SITL...!")
                print("connnection failed")
                exit()
                return False
            else:
                logging.info("MAVlink Connected to SITL successfully...!!")
                print("Heart Beat recieved")
                return True
            
        except Exception as e:
            logging.error(f"Error occured while SITL Connection: {e}")
            exit()
            return False

    
    def takeoff(self):
        print("Takeoff in a seconds")
        time.sleep(1)
        master.mav.command_long_send(
            master.target_system,
            master.target_component,
            mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
            0,
            0,0,0,0,0,0,
            10                 # -> altitude(idk)
        )

    def get_altitude(self) -> bool:
        msg : float= master.recv_match(
                type = 'GLOBAL_POSITION_INT',
                blocking = False,
            )
        if msg is None:
            return 0.0
        altitude = msg.relative_alt / 1000.0
        return altitude 
    
    def is_flying(self):
        altitude = self.get_altitude()
        return altitude > 1.0

    def arm(self):
        master.mav.command_long_send(
            master.target_system,
            master.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0,
            1,
            0,0,0,0,0,0
        )

    def setmode(self : Self, mode : str):
        mode_id = master.mode_mapping()[mode]
        master.mav.set_mode_send(
                master.target_system,
                mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
                mode_id,
            )
        
    def rc_channels_control(self: Self,
                            roll : int,
                            pitch : int,
                            throttle : int,
                            yaw : int,
                    ) -> None:
            if args.controller:
                self.roll = roll
                self.pitch = pitch
                self.throttle = throttle
                self.yaw = yaw

            master.mav.rc_channels_override_send(
                        master.target_system,
                        master.target_component,
                        self.roll,
                        self.pitch,
                        self.throttle,
                        self.yaw,
                        0,0,0,0
                    )
            


class Detection:

    def __init__(self : Self, sitl : Sitl):
        self.sitl = sitl

    def human_detection(self : Self, frame : np.ndarray):
        #Tracking

        results = model.track(
                    source = frame,
                    persist = True,
                    classes = [0],
                    verbose = False
                )
        
        loiter : bool = False
        if len(results[0].boxes) >0:
            print("Human detected.. Check for Dimension")
        #--------------------------checking dimension of the object-----------------------
            for result in results:
                boxes = result.boxes

                for box in boxes:
                    x, y, width, height = box.xywh.tolist()[0]
                    if width > 500.0:
                        print("Human is close to the UAV.. get to loiter")
                        print(f"latest dimension : x,y:({x:.2f},{y:.2f}) and w,h:({width:.2f},{height:.2f})")
                        mode = "LOITER"
                        loiter = True
                        self.command_send(mode)
                        break
                        
        return results[0].plot(),loiter

    """
    Below is an commands send to an SITL - controller file
        - which can control the drone with return commands
        - Additional functionality might be added in future
    """

    def command_send(self : Self, mode : str):
        if mode == "LOITER":                                   #In future might use many modes 
            result = self.sitl.setmode(mode)

# ------------ Controller ----------
key_held : Set = set()


def on_press(key : str):     # key - character 
    try: 
        key_held.add(key)

    except AttributeError:
        key_held.add(key)           # add special keys

def on_release(key):
    try:
        key_held.discard(key)

    except:
        key_held.discard(key)

# --------RC channel inputs----------

NEUTRAL = 1500
STEP = 200

def get_rc_channels() -> List:
    pitch = NEUTRAL
    roll  = NEUTRAL
    throttle = NEUTRAL
    yaw = NEUTRAL

    if 'w' in key_held:    pitch += STEP
    if 's' in key_held:    pitch -= STEP
    if 'a' in key_held:    roll  -= STEP
    if 'd' in key_held:    roll  += STEP
    if 'q' in key_held:    yaw   -= STEP
    if 'e' in key_held:    yaw   += STEP

    if keyboard.Key.up in key_held: throttle += STEP
    if keyboard.Key.down in key_held: throttle -= STEP

    if "c" in key_held:     Capture()

    return [
        max(1000, min(2000, roll)),
        max(1000, min(2000, pitch)),
        max(1000, min(2000, throttle)),
        max(1000, min(2000, yaw)),
        ]

def rc_override_loop(sitl : Sitl):
        while True:
            rc_inputs = get_rc_channels()
            sitl.rc_channels_control(*rc_inputs)
            time.sleep(0.1)

#--Capturing--
def Capture() -> None:         # to get frames and pass it for the  detections 
    #Use the webcam to do detection! channel --> 0
    cap = cv.VideoCapture(0)
    detection = Detection(sitl)
    if cap.isOpened():
        print("Capturing Work Successful!!")

    while True:
        ret, frame = cap.read()
        if not ret:
            logging.error("Can't capture the webCam Frame")
            break
        
        frame = cv.flip(frame, 1)
        detected_frame, loiter = detection.human_detection(frame)
        cv.imshow("Live Detections", detected_frame)

        if cv.waitKey(1) & 0xFF == ord("*"):
            print("KeyBoard interruption occur!!")
            break
        elif loiter:
            print("Break due to human detected, get into Loiter ")
            break
    cap.release()

#-------------------------------------------------------------------------------------------------!
if __name__ == '__main__':
#Creating connection with Drone or SITL controller 
         
    sitl = Sitl(
                args.roll,
                args.pitch,
                args.throttle,
                args.yaw
            )

    connection = sitl.create_connection()
    if connection:
        print("SITL is setup successfully!!")

#--------------------------
# Getting into guided mode
#--------------------------
    mode = "GUIDED"
    mode_id = master.mode_mapping()[mode]
    master.mav.set_mode_send(
        master.target_system,
        mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
        mode_id,
    )
#Preparing Drone .. & .. Check whether the drone is flying or not
    if not sitl.is_flying():
        sitl.arm()
        master.motors_armed_wait()
        sitl.takeoff()
    else:
        print("Drone is Already Flying. No need for takeoff")
    
    start = time.time()
    while True:
        altitude : float = sitl.get_altitude()
        print(f"Altitude: {altitude:.1f}m")
        if altitude > 10.0:
            print("Altitude Reached... Ready for RC control")
            break
        if time.time() - start > 30:
            print("Aborting Takeoff due to timeout")
            break
        time.sleep(0.5)
    
#------------------------------------------------------------------------
#change to ALT_HOLD mode for RC channel control
    mode = "ALT_HOLD"
    mode_id = master.mode_mapping()[mode]
    master.mav.set_mode_send(
                master.target_system,
                mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
                mode_id,
            )

    listener = keyboard.Listener(on_press = on_press, on_release = on_release)
    listener.start()

# ----------Thread for RC override loop--------------------
    rc_thread = threading.Thread(
                                target = rc_override_loop,
                                args = (sitl,),
                                daemon = False
                            )
    rc_thread.start()
#-------------------------------------------------------------------------
cv.destroyAllWindows()

# -----------------State of the project--------------------
"""
1.
    CURRENT-
    Try to stop the drone in the position, when it detects human very nearly
    Now it happens based on width of the box, but it is not the optimised method.

    NEXT-
    Try to do this based on distance between the object and the drone.
    by the mathematical expression-
            
                            {distance b/w XR & XL} x Focal length
                Distance = -------------------------------
                                    Pixel Width
            --------------------------> but this can't achieve without the stereo camera
2.
    Try to built an real time controller from the key board or any external console 
        
"""