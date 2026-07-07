from logger import logger 
from waypoint import waypoint
import quad
import connection

master = connection.get_master()
heartbeat = connection.get_heartbeat()

print(master)
if heartbeat is None:
    logger.error("Cant hear the HeartBeat......!!")

quad.setmode("GUIDED")
quad.arm()
master.motors_armed_wait()
quad.takeoff()
quad.land()

if __name__ == "__main__":
    pass