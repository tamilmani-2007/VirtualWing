import time
from pymavlink import mavutil
from quad import connection 
from quad.state import state

master = connection.get_master()

def isFlying():
    altitude = state.alt
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

def takeoff(alt : float):
    print("Takeoff in a seconds")
    master.mav.command_long_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
        0,
        0,0,0,0,0,0,
        alt                 # -> altitude(idk)
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