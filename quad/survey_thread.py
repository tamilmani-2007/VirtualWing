import threading
import time
from utils.logger import logger 
from quad import connection, quad, survey, state
from checks import checks

state = state.get_state()

class SurveyFlight(threading.Thread):
    def __init__(self):
        super().__init__(name = "Survey Thread")
    
    def run(self):
        print("Flight survey thread entered...")
        master = connection.get_master()

        PRE_ARM_CHECK, CHECKS = checks.check_for_preArm()
        print(CHECKS)
        print("-" * 30)
        
        if PRE_ARM_CHECK:
            print("Connection passed")

            if not quad.isFlying():
                quad.setmode("GUIDED")
                quad.arm()
                
                while not state.armed:
                    time.sleep(0.1)

                print("Drone armed")

                quad.takeoff(50.0)

                while True:
                    altitude = state.alt
                    if altitude >= 50.0:
                        print("altitude reached")
                        break
                    time.sleep(0.5)

                print("Entering into survey mode")
                survey.start_survey()
            else:
                print("Drone is in Flight, Land and try again")

