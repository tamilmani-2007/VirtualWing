from utils.logger import logger
from quad.connection import get_master,get_heartbeat
from typing import (Dict,
                    List,
                    )
from collections import defaultdict 

# Checks needed for the pre Arm 
CONNECTION : bool = False
HEARTBEAT : bool = False
PRE_ARM_CHECK : bool = False
CHECKS : Dict[str, bool] = defaultdict(list)

def check_for_preArm():
    """
    Check for the pre Arm to check the drone is ready to fly or not.
    This contains the basic functionality checks needed
    """
    if get_master() and get_heartbeat():
        CONNECTION = True
        HEARTBEAT = True
    
    if all([CONNECTION,
            HEARTBEAT]
            ):
        PRE_ARM_CHECK =True

    CHECKS.update({
            "CONNECTION" : True,          
            "HEARTBEAT" : True
            })
        
    return PRE_ARM_CHECK, CHECKS
 
def survey_check():
    pass