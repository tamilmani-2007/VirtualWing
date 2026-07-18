from quad.survey_thread import SurveyFlight 

"""
I did only the survey part of the Drone.
Next is the vision part of the Drone
"""
def main():
    survey = SurveyFlight()
    survey.start()
    survey.join()

    print("Mission accomplished..")

if __name__ == "__main__":
    main()