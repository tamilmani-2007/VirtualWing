import const
import pyproj
from pyproj import Transformer, CRS
from typing import (
                List,
                TypeAlias
                )
from shapely import Polygon, LineString, get_coordinates
import math

#----------Camera Details in mm------------------------
FOCAL_LENGTH = 0.0088
SENSOR_WIDTH = 0.0132
SENSOR_HEIGHT = 0.0088

#----------Overlapping in percentage-------------------
SIDE_OVERLAP = 0.70
FRONT_OVERLAP = 0.80

#----------Relative altitude of drone in m-------------
FLIGHT_ALTITUDE = 50

polygon = const.polygon
polygon_in_meters = []

#-----------Typing mention-----------------------------
Radian : TypeAlias = float
Meters : TypeAlias = float

def get_utm_zone(lat, lon):
    """
        Get the UTM zone for the given lat and lon
    """
    zone = int(math.floor((lon + 180) / 6)) + 1
    hemisphere : str = "north" if lat >= 0 else "south"

    return zone, hemisphere

def gps_to_meter(lat, lon):
    zone, hemisphere = get_utm_zone(lat, lon)

    src_crs = CRS.from_epsg(4326)

    proj_str = f" +proj=utm +zone={zone} +datum=WGS84 +units=m +nodefs"
    if hemisphere == "south":
        proj_str += "south"
    
    trg_src = CRS.from_proj4(proj_str)

    transformer = Transformer.from_crs(src_crs, trg_src, always_xy = True)
    easting, northing = transformer.transform(lat, lon)
    return easting, northing, hemisphere

for coordinate in polygon:
    easting, northing, _ = gps_to_meter(coordinate[0],coordinate[1])
    coord_in_meter = (easting, northing)
    polygon_in_meters.append(coord_in_meter)

polygon_shape = Polygon(polygon_in_meters)
num_points = len(polygon_in_meters)

def Bounding_box():
    x_values = [p[0] for p in polygon_in_meters]
    y_values = [p[1] for p in polygon_in_meters]

    min_x = min(x_values)
    max_x = max(x_values)

    min_y = min(y_values)
    max_y = max(y_values)

    bounding_box = Polygon([(min_x, min_y),
                            (max_x, min_y),
                            (max_x, max_y),
                            (min_x, max_y)
                            ])
    coordinates = [min_x, min_y, max_x, max_y]
    return bounding_box, coordinates

def get_linespace() -> Meters:
    GROUND_WIDTH = (FLIGHT_ALTITUDE * SENSOR_WIDTH) / FOCAL_LENGTH
    LINE_SPACING = GROUND_WIDTH * (1 - SIDE_OVERLAP)

    return LINE_SPACING

def get_survey_area():
    line_spacing = get_linespace()
    bounding_box, coordinates = Bounding_box()
    min_x, min_y, max_x, max_y = coordinates
    current_y = max_y

    # line = LineString([
    #             (min_x, current_y),
    #             (max_x, cuurent_y)
    #             ])

def slope_of_large_edge() -> float:
    edge_distances : List[float]= []
    slopes = []                 # to find the largest edge ange

    for i in range(num_points):
        p1 = polygon_in_meters[i]
        p2 = polygon_in_meters[(i+1) % num_points]

        distance = math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
        edge_distances.append(distance)
        slope = (p2[1] - p1[1]) / (p2[0] - p1[0])
        slopes.append(slope)

    largest_edge = edge_distances.index(max(edge_distances))
    largest_edge_slope = slopes[largest_edge]

    return largest_edge_slope

def get_rotaion_angle() -> Radian:
    slope = slope_of_large_edge()
    angle_rad = math.atan(slope)
    return angle_rad

def rotate_the_polygon() -> List[tuple]:
    rotated_polygon : List[tuple] = []
    angle = get_rotaion_angle()
    
    for x,y in polygon_in_meters:
        xr = x * math.cos(angle) - y * math.sin(angle)
        yr = x * math.sin(angle) + y * math.cos(angle)
        rotated_point = (xr, yr)
        rotated_polygon.append(rotated_point)
    return rotated_polygon


