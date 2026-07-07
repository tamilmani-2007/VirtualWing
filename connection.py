from pymavlink import mavutil

master = None

def get_master():
    global master
    if master is None:
        connection_string : str = "udp:127.0.0.1:14552"
        master = mavutil.mavlink_connection(connection_string)

    return master

def get_heartbeat():
    return master.wait_heartbeat( timeout= 10)


