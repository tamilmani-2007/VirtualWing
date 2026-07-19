"""
the object "state" created for the DroneState is created for sharing
informations of Drone state simultaneously over other classes
"""

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

state = DroneState()

def get_state():
    return state