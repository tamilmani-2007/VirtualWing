import connection 
import time
from pymavlink import mavutil

master = connection.get_master()

def get_altitude() -> bool:
    msg : float= master.recv_match(
            type = 'GLOBAL_POSITION_INT',
            blocking = False,
        )
    if msg is None:
        return 0.0
    altitude = msg.relative_alt / 1000.0
    return altitude 

def is_flying():
    altitude =get_altitude()
    return altitude > 1.0

def arm():
    master.mav.command_long_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        0,
        1,
        0,0,0,0,0,0
    )

def disarm():
    master.mav.command_long_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        0,
        0,
        0,0,0,0,0,0
     )

def takeoff():
    print("Takeoff in a seconds")
    master.mav.command_long_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
        0,
        0,0,0,0,0,0,
        10                 # -> altitude(idk)
    )


def setmode(mode : str):
    mode_id = master.mode_mapping()[mode]
    master.mav.set_mode_send(
            master.target_system,
            mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
            mode_id,
        )
def land():
    master.mav.command_long_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_CMD_NAV_LAND,
        0,
        0,0,0,0,
        0,0,0    # third-0 is for the altitude 0- landing
    )