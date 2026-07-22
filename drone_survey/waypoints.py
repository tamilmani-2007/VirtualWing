from .const import polygon
import pyproj
from pyproj import Transformer, CRS
from typing import (
                List,
                TypeAlias,
                Self
                )
from shapely import Polygon, LineString
import math
from utils.logger import logger
import matplotlib.pyplot as plt

#-----------Typing mention-----------------------------

Radian : TypeAlias = float
Meters : TypeAlias = float

#----------Camera Specifications in mm------------------------
FOCAL_LENGTH = 0.0088
SENSOR_WIDTH = 0.0132
SENSOR_HEIGHT = 0.0088

#----------Overlapping in percentage-------------------
SIDE_OVERLAP = 0.70
FRONT_OVERLAP = 0.80

#----------Relative altitude of drone in m-------------
FLIGHT_ALTITUDE = 50
#------------------Rotate polygon togles---------------
ROTATE_POLYGON_REVERSE = False
"""
    We need to rotate the polygon two times.
    1st time - rotate the polygon to make the largest edge parallel with the x-axis
    2nd time - reverse the process to do set longitude and lattitude
"""

"""
polygon_in_meter is store the points for the first rotation
"""

def get_linespace() -> Meters:
    GROUND_WIDTH = (FLIGHT_ALTITUDE * SENSOR_WIDTH) / FOCAL_LENGTH
    LINE_SPACING = GROUND_WIDTH * (1 - SIDE_OVERLAP)

    return LINE_SPACING

class CoordinateTransformer:
    def __init__(self, lat : float, lon : float):
        zone, hemisphere = self.get_utm_zone(lat, lon)

        self.src_crs = CRS.from_epsg(4326)

        proj_str = f" +proj=utm +zone={zone} +datum=WGS84 +units=m +nodefs"
        if hemisphere == "south":
            proj_str += " south"
        
        self.utm_crs = CRS.from_proj4(proj_str)

        self.gps_to_utm = Transformer.from_crs(
                         self.src_crs,
                         self.utm_crs,
                         always_xy = True
                            )
        self.utm_to_gps = Transformer.from_crs(
                         self.utm_crs,
                         self.src_crs,
                         always_xy = True
                            )
    
    @staticmethod
    def get_utm_zone(lat, lon):
        """
            Get the UTM zone for the given lat 
        """
        zone = int(math.floor((lon + 180) / 6)) + 1
        hemisphere : str = "north" if lat >= 0 else "south"

        return zone, hemisphere

    def gps_to_meter(self, lat, lon):
       easting, northing = self.gps_to_utm.transform(
                                lon,
                                lat
                                )
       return easting, northing
    
    def meter_to_gps(self, easting, northing):
        lon, lat = self.utm_to_gps.transform(
                                easting,
                                northing
                                )
        return lat, lon

"""
 used to prepare the transformer for the UTM zone,
 So only one point of lat and lon is enough to determine and prepare the transformer 
"""     
class SurveyPlanner:
    def __init__(self : Self,
                polygon : List[tuple]
            ):
                
                self.polygon = polygon
                self.polygon_shape = Polygon(polygon)
                self.rotation_angle = self.get_rotaion_angle()
                self.rotated_area = self.rotate_points(self.polygon,
                                                    ROTATE_POLYGON_REVERSE = False
                                                    )             # -> It is just the coordinates of the rotated polygon. Not the shape itself
                self.rotated_area_shape = Polygon(self.rotated_area)

    def longest_edge(
            self : Self
            ) -> tuple[float, float, float]:
                
                max_Edgelength = 0    
                num_points = len(self.polygon)
                for i in range(num_points):
                    p1 = self.polygon[i]
                    p2 = self.polygon[(i+1) % num_points]

                    edge_distance = math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
                    dy = p2[1] - p1[1]
                    dx = p2[0] - p1[0]

                    if edge_distance > max_Edgelength:
                        max_Edgelength = edge_distance
                        long_dx = dx
                        long_dy = dy
                
                return long_dy, long_dx, max_Edgelength
        
    def get_rotaion_angle(
            self : Self
            ) -> Radian:
                
                dy, dx, _ = self.longest_edge()
                angle_rad = math.atan2(dy, dx)
                return angle_rad

    def rotate_points(
            self : Self,
            points : List[tuple], 
            ROTATE_POLYGON_REVERSE : bool
            ) -> List[tuple]:
                
                rotated_polygon : List[tuple] = []

                if ROTATE_POLYGON_REVERSE:                   # For the second time rotation
                    angle = self.rotation_angle
                else:
                    angle = -self.rotation_angle               # For the first time rotation

                cx = self.polygon_shape.centroid.x
                cy = self.polygon_shape.centroid.y

                for x,y in points:
                    x = x - cx
                    y = y - cy

                    xr = x * math.cos(angle) - y * math.sin(angle)
                    yr = x * math.sin(angle) + y * math.cos(angle)

                    xr = xr + cx
                    yr = yr + cy

                    rotated_point = (xr, yr)
                    rotated_polygon.append(rotated_point)
                
                return rotated_polygon

    def bounding_box(
              self : Self
            ) -> tuple[Polygon, List]:
                
                x_values = [p[0] for p in self.rotated_area]
                y_values = [p[1] for p in self.rotated_area]

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


    def generate_survey_lines(
                self : Self
            ) -> List[LineString]:

                line_spacing = get_linespace()
                bounding_box, coordinates = self.bounding_box()

                min_x, min_y, max_x, max_y = coordinates
                current_y = max_y
                margin = 100
                survey_lines = []

                while current_y >= min_y:
                    line = LineString([
                                (min_x - margin, current_y),
                                (max_x + margin, current_y)
                                ])
                    survey_lines.append(line)

                    current_y -= line_spacing

                return survey_lines

    def get_instersections(
                self : Self
            ) -> List[tuple]:
                
                intersection_points : List[tuple] = []
                survey_lines = self.generate_survey_lines()

                for line in survey_lines:
                    intersection = self.rotated_area_shape.intersection(line)

                    if intersection.is_empty:
                        continue
                    coords = list(intersection.coords)
                    start = coords[0]
                    end = coords[-1]

                    intersection_points.append((start, end))

                return intersection_points

    def survey_path(
                self : Self
            ) -> List[tuple]:
                
                path = []
                reverse = False
                intersections = self.get_instersections()
            
                for start, end in intersections:
                    if reverse:
                        path.append(end)
                        path.append(start)
                    else:
                        path.append(start)
                        path.append(end)
                    
                    reverse = not reverse
                return path
    
class Plotter:
    def __init__(
                self : Self,
                planner : SurveyPlanner,
                survey_path : List[tuple]
            ):
                self.planner = planner
                self.survey_path = survey_path
    def plot_xy(
                self : Self,
                points : List[tuple],
                closing : bool
            ) -> tuple[List, List]:

                x = [p[0] for p in points]
                y = [p[1] for p in points]

                if closing:
                    x.append(points[0][0])
                    y.append(points[0][1])

                return x, y

    def plot_original_polygon(
                self : Self,
                ax, 
            ) -> None:
                x, y = self.plot_xy(
                       self.planner.polygon,
                       closing = True
                            )
                ax[0,0].plot(x, y)
                ax[0,0].set_title("Original")

    def plot_rotated_polygon(
                self : Self,
                ax,   
            ) -> None:
                x, y = self.plot_xy(
                        self.planner.rotated_area,
                        closing = True
                            )
                ax[0,1].plot(x, y)
                ax[0,1].set_title("Rotated")

    def plot_survey_lines(
                  self : Self,
                  ax
            ) -> None:
                for line in self.planner.generate_survey_lines():
                       x, y = line.xy
                       ax[0,2].plot(x,y)

                ax[0,2].set_title("Survey lines")
    def plot_intersection(
                  self : Self,
                  ax
            ) -> None:
                
                for start, end in self.planner.get_instersections():
                       ax[1,0].plot(
                            [start[0], end[0]],
                            [start[1], end[1]],
                            linewidth = 3  
                            )
    
    def plot_path(
                  self : Self,
                  ax
            ) -> None:
                  x, y = self.plot_xy(
                         self.survey_path,
                         closing = False
                    ) 
                  ax[1,1].plot(x, y)
                  ax[1,1].set_title("Survey Path")

    def plot_all(
                self : Self      
            ):
                fg, ax = plt.subplots(2,3)
                self.plot_original_polygon(ax)
                self.plot_rotated_polygon(ax)
                self.plot_survey_lines(ax)
                self.plot_intersection(ax)
                self.plot_path(ax)

                plt.tight_layout()
                plt.show()
   
#--------------------------------------------

polygon_in_meters : List[tuple]= []
first_lat, first_lon = polygon[0]

# resultant gps position for the survey of the intersections
gps_pos : List[tuple] = []
CoordTrans = CoordinateTransformer(first_lat, first_lon)

for coordinate in polygon:
    easting, northing = CoordTrans.gps_to_meter(
                            coordinate[0],
                            coordinate[1]
                        )
    coord_in_meter = (easting, northing)
    polygon_in_meters.append(coord_in_meter)

planner = SurveyPlanner(polygon_in_meters)
path = planner.survey_path()          # path for the survey before the rotation

survey_area = planner.rotate_points(
                            path,
                            ROTATE_POLYGON_REVERSE = True
                        )

for coordinate in survey_area:
    lat, lon = CoordTrans.meter_to_gps(
                            coordinate[0],
                            coordinate[1]
                        )
    coord_in_gps = (lat, lon)
    gps_pos.append(coord_in_gps)

rotated_polygon = planner.rotated_area

plotter = Plotter(
            planner,
            survey_area
        )

"""
Need to add the buffer operations if the border has fence.
we need to turn the drone before fence nearly 1m - 3m early
"""
       
def get_resultant_gps_pos() -> List[tuple]:
     return gps_pos

def survey_plot():
       return plotter