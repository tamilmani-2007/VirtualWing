"""
the object "state" created for the DroneState is created for sharing
informations of Drone state simultaneously over other classes
"""
from typing import List

class DroneState:
    def __init__(self):
        self.lat = None
        self.lon = None
        self.alt = None
        self.heading = None
        self.speed = None
        self.armed = None
        self.mode = None
        self.connected = False
        self.heartbeat = False
        self.is_survey_completed = False
        self.survey_mission = True
        self.geotags : List[tuple] = []

state = DroneState()

def get_state():
    return state