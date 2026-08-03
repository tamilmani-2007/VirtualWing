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
            if not ret:
                logger.warning("Can't capture the frame")
                break
            frame = cv.flip(frame, 1)

            detected_frame = detector.detect(frame)[0]      
            
            cv.imshow("detected frame", detected_frame.plot())
        
            for box in detected_frame.boxes:

                if box.id is None:
                    continue

                track_id = int(box.id.item())
                
                if track_id in state.processed_ids:
                    continue
                else:
                    geotag.geotag(box)

                state.processed_ids.add(track_id)

            cv.waitKey(1)
        
        cap.release()
        cv.destroyAllWindows()