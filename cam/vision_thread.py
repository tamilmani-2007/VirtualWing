"""
I didn't decide the flow of capturing and processing yet.
Will be conclude and sort out in the next push 
"""

import cv2 as cv
import threading
from utils.logger import logger
from quad.state import state

CAMERA_SOURCE = 0

class VisionThread(threading.Thread):
    def __init__(self):
        super().__init__(name = "Vision Thread")
        self.running = True

    def stop(self):
        self.running = False
    
    def run(self):
        cap = cv.VideoCapture(CAMERA_SOURCE)
        print("hello")
        while state.survey_mission:
            ret, frame = cap.read()

            if not ret:
                logger.warning("Can't capture the frame")
                break
            frame = cv.flip(frame, 1)
            cv.imshow("webcam", frame)

            cv.waitKey(1)
        
        cap.release()
        cv.destroyAllWindows()