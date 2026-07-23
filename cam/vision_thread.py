"""
I didn't decide the flow of capturing and processing yet.
Will be conclude and sort out in the next push 
"""

import cv2 as cv
import threading
from utils.logger import logger
from quad.state import state
from cam.obj_detect import Detector
from drone_survey.geotag import GeoTag
from quad.survey import harvasine

CAMERA_SOURCE = 0

geotag = GeoTag()

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

            if not ret:
                logger.warning("Can't capture the frame")
                break

            detected_frame = detector.detect(frame)
            if len(detected_frame.boxes) != 0:
                tag = geotag.geotag(detected_frame)
                for pos in state.geotags:
                    if not harvasine(pos[0], pos[1], state.lat, state.lon) <= 4:
                        state.geotags.append(tag)            
            
            cv.imshow("detected frame", detected_frame[0].plot())

            cv.waitKey(1)
        
        cap.release()
        cv.destroyAllWindows()