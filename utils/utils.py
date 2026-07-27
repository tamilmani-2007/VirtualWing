CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_HORIZONTAL_FOV = 80
CAMERA_VERTICAL_FOV = 60


#----------Camera Specifications in mm------------------------
FOCAL_LENGTH = 0.0088
SENSOR_WIDTH = 0.0132
SENSOR_HEIGHT = 0.0088

#----------Overlapping in percentage-------------------
SIDE_OVERLAP = 0.70
FRONT_OVERLAP = 0.80

#----------Relative altitude of drone in m-------------
FLIGHT_ALTITUDE = 50

def ground_width_height():
    GROUND_WIDTH = (FLIGHT_ALTITUDE * SENSOR_WIDTH) / FOCAL_LENGTH
    GROUND_HEIGHT = (FLIGHT_ALTITUDE * SENSOR_HEIGHT) / FOCAL_LENGTH
    
    return GROUND_WIDTH, GROUND_HEIGHT

def get_pixel_length():
    GROUND_WIDTH, GROUND_HEIGHT = ground_width_height()
    GROUND_PIXEL_WIDTH = GROUND_WIDTH / CAMERA_WIDTH
    GROUND_PIXEL_HEIGHT = GROUND_HEIGHT / CAMERA_HEIGHT

    return GROUND_PIXEL_WIDTH, GROUND_PIXEL_HEIGHT

def calculate_offset(x_pixels, y_pixels):
    GROUND_PIXEL_WIDTH, GROUND_PIXEL_HEIGHT = get_pixel_length()
    easting_distance = x_pixels * GROUND_PIXEL_WIDTH
    northing_distance = y_pixels * GROUND_PIXEL_HEIGHT

    return easting_distance, northing_distance
    