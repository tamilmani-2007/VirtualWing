"""
Here I created the telemetry thread to get the messages from the drone.

this informations are transferred to the state object. 
"""
import threading
from utils.logger import logger
from quad import connection
from quad.state import get_state 
from pymavlink import mavutil

state = get_state()
master = connection.get_master()

class TelemetryThread(threading.Thread):
    def __init__(self):
        super().__init__(name = "Vision Thread")
        self.running = True

    def stop(self):
        self.running = False

    def run(self):
        while self.running:
            msg = master.recv_match(
                            type = [
                                "HEARTBEAT",
                                "GLOBAL_POSITION_INT",
                                "VFR_HUD"
                            ],
                            blocking = True,
                            timeout = 5)
            if not msg:
                logger.warning("Cant get the message from the drone!!")
                continue

            msg_type = msg.get_type()

            if msg_type == "GLOBAL_POSITION_INT":
                state.lat = msg.lat / 1e7
                state.lon = msg.lon / 1e7
                state.alt = msg.relative_alt / 1000
                state.heading = msg.hdg / 100
            
            elif msg_type == "HEARTBEAT":
                state.heartbeat = True
                state.mode = mavutil.mode_string_v10(msg)

                state.armed = (
                    msg.base_mode &
                    mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED
                ) != 0
            elif msg_type == "VFR_HUD":
                state.speed = msg.groundspeed

                