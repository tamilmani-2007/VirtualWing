import threading
import time
from utils.logger import logger 
from quad import connection, quad, survey
from checks import checks


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
                master.motors_armed_wait()
                quad.takeoff(50.0)

                while True:
                    altitude = quad.get_altitude()
                    if altitude >= 50.0:
                        print("altitude reached")
                        break
                    time.sleep(0.5)

                print("Entering into survey mode")
                survey.start_survey()

