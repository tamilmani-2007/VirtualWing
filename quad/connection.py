from pymavlink import mavutil
from utils.logger import logger 

master = None
connection = False
def get_master():
    global master
    if master is None:
        connection_string : str = "udp:127.0.0.1:14552"
        master = mavutil.mavlink_connection(connection_string)
    connection = True
    return master

def get_heartbeat():
    try:
        return master.wait_heartbeat(timeout= 10)
    except Exception:
        print("-" * 50)
        logger.error("Could not connect to the Drone")

