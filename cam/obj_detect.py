from ultralytics import YOLO
from typing import Self
import numpy as np

class Detector:
    def __init__(
            self : Self
            ) -> None:
                self.model = YOLO("yolov8n.pt")
    
    def detect(
            self : Self,
            frame : np.ndarray
            ) -> np.ndarray:
            return self.model(
                frame,
                verbose = False
            )[0].plot()
