import time
from utils.logger import logger
from quad.connection import get_master
from quad.state import state
from quad.survey_thread import SurveyFlight 
from quad.telemetry_thread import TelemetryThread
from cam.vision_thread import VisionThread
from quad import quad

"""
I did only the survey part of the Drone.
Next is the vision part of the Drone
"""

def main():
    if get_master():
        state.connected = True

    telemetry = TelemetryThread()
    vision = VisionThread()
    survey = SurveyFlight()

    print("Heartbeat Recieved")
    try:
        telemetry.start()
        #------Checking Heartbeat -> Pre-requesity for the survey
        print("wait for the heartbeat")

        while not state.heartbeat:
            time.sleep(0.1)

        vision.start()
        survey.start()

        survey.join()
    except KeyboardInterrupt:
        logger.error("Keyboard Interruption Occur!..")
        print("Enter into RTL")
        quad.setmode("RTL")
        state.survey_mission = False

    finally:
        vision.stop()
        telemetry.stop()

        vision.join()
        telemetry.join()

    if state.is_survey_completed:
        print("Mission accomplished..")

if __name__ == "__main__":
    main()