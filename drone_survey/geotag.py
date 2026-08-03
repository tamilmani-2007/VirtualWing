"""
Here I will do some mathematical calculation,
To get the Geo-location of the detected object
"""
from quad.state import get_state
from drone_survey.waypoints import CoordinateTransformer
from utils import utils
from quad.survey import harvasine
from drone_survey.waypoints import get_CoordTrans
from ultralytics import YOLO
import math

model = YOLO("yolov8n.pt")

state = get_state()  

CoordTrans = get_CoordTrans()


GROUND_WIDTH, GROUND_HEIGHT = utils.ground_width_height()

frame_center_x, frame_center_y = utils.CAMERA_WIDTH/ 2  , utils.CAMERA_HEIGHT / 2 
pixel_length = 0

class GeoTag:
    def __init__(self):
        self.pixel_length = utils.get_pixel_length()

    def geotag(self, box):
        current_lat, current_lon = state.lat, state.lon
        current_lat_m, current_lon_m = CoordTrans.gps_to_meter(
                                                                    current_lat,
                                                                    current_lon 
                                                                )
        x_center, y_center, _, _ = box.xywh[0].cpu().tolist()

        pixel_diff_x = x_center - frame_center_x
        pixel_diff_y = y_center - frame_center_y
    
        x_offset, y_offset = utils.calculate_offset(pixel_diff_x, pixel_diff_y)

        obj_lon_m = current_lon_m + x_offset
        obj_lat_m = current_lat_m + y_offset

        obj_lat, obj_lon  = CoordTrans.meter_to_gps(obj_lon_m, obj_lat_m)

        state.geotags.append((obj_lat, obj_lon))
        print("lat, lon:", obj_lat, obj_lon)