import math
import time 

from utils.logger import logger 
from typing import Dict
from pymavlink import mavutil 
from drone_survey.waypoints import get_resultant_gps_pos
from quad.connection import master
from quad import quad
from quad.state import get_state

state = get_state()

gps_pos = get_resultant_gps_pos()

WAYPOINT_TOLERANCE = 2.0 
EARTH_RADIUS = 63721000
SURVEY_ALTITUDE = 50.0


def goto(
        lat,
        lon
    ) -> None:
    master.mav.set_position_target_global_int_send(
        0,
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
        0b110111111000,
        int(lat * 1e7),
        int(lon * 1e7),
        SURVEY_ALTITUDE,
        0,0,0,
        0,0,0,
        0,0      
    )

def harvasine(
            lat1,
            lon1,
            lat2,
            lon2
        ) -> float:
    dLat = (lat2 - lat1) * math.pi / 180.0
    dLon = (lon2 - lon1) * math.pi / 180.0

    lat1 = (lat1) * math.pi / 180.0
    lat2 = (lat2) * math.pi / 180.0

    a = (
        pow(math.sin(dLat / 2), 2) +
        pow(math.sin(dLon / 2), 2) *
        math.cos(lat1)* math.cos(lat2)
    )
    
    c = 2 * math.asin(math.sqrt(a))
    return EARTH_RADIUS * c

def wait_until_reached(target_lat, target_lon, tolerance = WAYPOINT_TOLERANCE):
    
    while state.survey_mission:
        lat, lon = state.lat, state.lon

        distance = harvasine(
            lat,
            lon,
            target_lat,
            target_lon
        )
        print(f"Distance: {distance:.2f} m")
        
        if distance <= tolerance:
            break
        time.sleep(0.5)
        
    print("-" * 20, "\n")
    
def start_survey():
    for i, (lat, lon) in enumerate(gps_pos, start = 1):
        goto(lat, lon)
        wait_until_reached(lat, lon)
        print(f"Waypoint reached : {i}")
        last = i

    if last == len(gps_pos):
        print("Survey finished")
        print("-" * 20)
        print("Enter into the RTL mode")
        quad.setmode("RTL")
        state.is_survey_completed = True


