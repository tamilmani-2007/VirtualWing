import time
from utils.logger import logger 
from quad import connection, quad, survey
from checks import checks

master = connection.get_master()
heartbeat = connection.get_heartbeat()


if __name__ == "__main__":
    PRE_ARM_CHECK, CHECKS = checks.check_for_preArm()
    print(CHECKS)
    print("-" * 30)
    
    if PRE_ARM_CHECK:
        print("Connection passed")
        
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