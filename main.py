import time
from quad.connection import get_master
from quad.state import state
from quad.survey_thread import SurveyFlight 
from quad.telemetry_thread import TelemetryThread
"""
I did only the survey part of the Drone.
Next is the vision part of the Drone
"""
def main():
    if get_master():
        state.connected = True

    telemetry = TelemetryThread()

    print("State thread------->")
    telemetry.start()
    
    print("wait for the heartbeat")

    while not state.heartbeat:
        time.sleep(0.1)

    print("Heartbeat Recieved")

    survey = SurveyFlight()
    print("Survey Thread------>")
    survey.start()

    survey.join()

    telemetry.stop()
    telemetry.join()

    if state.is_survey_completed:
        print("Mission accomplished..")

if __name__ == "__main__":
    main()