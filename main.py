import time
from utils.logger import logger
from quad.connection import get_master
from quad.state import state
from quad.survey_thread import SurveyFlight 
from quad.telemetry_thread import TelemetryThread
from cam.vision_thread import VisionThread
from quad import quad
from checks.dup_geotag_check import rem_duplicate_tags
import argparse

def main():
  
    if get_master():
        state.connected = True

    telemetry = TelemetryThread()
    vision = VisionThread()
    survey = SurveyFlight()

    try:
        telemetry.start()
    
        #------Checking Heartbeat -> Pre-requesity for the survey
        print("wait for the heartbeat")

        while not state.heartbeat:
            time.sleep(0.1)

        print("Heartbeat Recieved")

        vision.start()
        survey.start()

        survey.join()
    except KeyboardInterrupt:
        logger.error("Keyboard Interruption Occur!..")
        print("Enter into RTL")
        quad.setmode("RTL")
        state.survey_mission = False

    finally:
        if (
            vision.is_alive(),
            telemetry.is_alive()
        ):
            vision.stop()
            telemetry.stop()

            vision.join()
            telemetry.join()

    if state.is_survey_completed:
        print("Mission accomplished..")

    print("Before removing Geotags")
    print(state.geotags)

    print("Removing duplication in geotags")    
    rem_duplicate_tags()
    
    print(state.geotags)
    

if __name__ == "__main__":
    main()