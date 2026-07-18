from pymavlink import mavutil
from utils.logger import logger 

master = None

def get_master():
    global master
    if master is None:
        connection_string : str = "udp:127.0.0.1:14552"
        master = mavutil.mavlink_connection(connection_string)
    
    return master

