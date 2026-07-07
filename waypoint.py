from logger import logger 
from typing import Dict
from pymavlink import mavutil 

def waypoint(master):
    # need to confirm drone is flying in the relative alt of above alt 10m
    
    # Set the GPS data from the Drone
    while True:
        GPSdata : Dict = master.recv_match( type = 'GLOBAL_POSITION_INT')
        if GPSdata is None:
            continue
        print(GPSdata)