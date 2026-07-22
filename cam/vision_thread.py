"""
I didn't decide the flow of capturing and processing yet.
Will be conclude and sort out in the next push 
"""

import cv2 as cv
import threading
from utils.logger import logger
from quad.state import state
from cam.obj_detect import Detector

CAMERA_SOURCE = 0

class VisionThread(threading.Thread):
    def __init__(self):
        super().__init__(name = "Vision Thread")
        self.running = True

    def stop(self):
        self.running = False
    
    def run(self):
        detector = Detector()
        cap = cv.VideoCapture(CAMERA_SOURCE)
        
        while state.survey_mission:
            ret, frame = cap.read()
            frame = cv.flip(frame, 1)

            detected_frame = detector.detect(frame)

            if not ret:
                logger.warning("Can't capture the frame")
                break
            cv.imshow("detected frame", detected_frame)

            cv.waitKey(1)
        
        cap.release()
        cv.destroyAllWindows()