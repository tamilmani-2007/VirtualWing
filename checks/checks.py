from utils.logger import logger
from quad.connection import get_master
from typing import (Dict,
                    List,
                    )
from collections import defaultdict
from quad.state import state 


def check_for_preArm():
    """
    Check for the pre Arm to check the drone is ready to fly or not.
    This contains the basic functionality checks needed
    """
    PRE_ARM_CHECK : bool = False
    CHECKS : Dict[str : bool] = {}

    if all([state.connected,
            state.heartbeat]
            ):
        PRE_ARM_CHECK =True

    CHECKS.update({
            "CONNECTION" : state.connected,          
            "HEARTBEAT" : state.heartbeat
            })
        
    return PRE_ARM_CHECK, CHECKS
 
def survey_check():
    pass