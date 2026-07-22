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

            if not quad.isFlying() and state.survey_mission:
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
                print("Drone is in Flight or the survey_mission is in False, Land and try again")

                ask_for_rtl = True

                while ask_for_rtl:
                    rtl = input("Can I Return to Launch on my own [y/n]")
                    if rtl.lower() == "y" or rtl.lower() == "":
                        print("Get to the Launch")
                        quad.setmode("RTL")
                        exit()
                    elif rtl.lower() == "n":
                        print("Okay..")
                        ask_for_rtl = False
                    else:
                        print("Invalid credential Given try [y/n]")
                        print("\n")


