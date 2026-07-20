from pymavlink import mavutil
from utils.logger import logger 
from drone_survey.const import port 

master = None

def get_master():
    global master
    
    if master is None:
        connection_string : str = f"udp:127.0.0.1:{port}"
        master = mavutil.mavlink_connection(connection_string)
    
    return master

