import os
import sys
import logging
from configparser import ConfigParser
from collections import deque
from typing import Optional
from multiprocessing import cpu_count
from concurrent.futures import (ThreadPoolExecutor,
                                as_completed
)

import geopandas as gpd
from shapely.geometry import Point, LineString
from shapely.ops import transform
import osmnx  as ox
import networkx as nx
from scipy import spatial
from pyproj.crs import CRS
import pyproj

from utils.pose import Pose
from utils.routes import Rails
from utils.objects import Objects
from utils.emulator import Emulator
from utils.routing import Routing
from utils.shared_memory import RamBox

config = ConfigParser()
config.read('config.ini')
config = config["main"]

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(message)s',
                    stream= sys.stdout)

os.chdir(config["path"])

class Navigator:
    """
    Navigator inits with one railway. 
    Railway update is not implemented yet.
    """
    def __init__(self):
        objects = Objects()
        rails = Rails()
        freq = 1
        
        self.emulator = Emulator(freq)
        self.pose: Pose = next(self.emulator) # first coord
        self.main_rail: gpd.GeoDataFrame = rails.get_closest_line(self.pose.coords)
        self.point_base: dict = self._init_point_base(objects = objects)

        self.router = Routing(pose = self.pose.coords)
        self.projection = self._init_transformer()

        self.points_tree = spatial.KDTree([
            (row.geometry.x, row.geometry.y)
            for _, row 
            in self._snap_points(objects.get_Points()).iterrows()
        ])

        self.shared_memory = RamBox("point_routing", role = "w")

        del objects
        del rails
    
    def _init_transformer(self):
        router_crs = CRS.from_user_input(self.router.CRS)
        wgs84 = pyproj.CRS('EPSG:4326')
        projection = pyproj.Transformer.from_crs(router_crs, wgs84, always_xy=True).transform
        return projection
    
    def _transformer(self, utm_obj):
        wgs84_obj = transform(self.projection, utm_obj)
        return wgs84_obj

    def _custom_rail(self, objects: Objects) -> LineString: 
        """ Point array -> Kd-tree -> tracing"""
        graph1: list = [(row.geometry.x, row.geometry.y,) for _, row in \
                                   self._snap_points(objects.get_Points()).iterrows()]
        graph2: list = [point for point in self.main_rail.geometry[0].coords]

        G = nx.MultiDiGraph()
        for seg_start, seg_end in zip(graph2, graph2[1:]):
            G.add_edge(seg_start, seg_end)

        graph_proj = ox.project_graph(G)
        print(graph_proj)

    def _init_point_base(self, objects: Objects) -> dict:
        """ initial points info to use """
        point_base = dict()
        counter = 0
        for idx, row in objects.get_Points().iterrows():
            point_base[counter] = [idx, row.geometry, row.Name, row.Description]
            counter += 1
        return point_base

    def _snap_points(self, points: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        points.geometry = points.apply(lambda row: \
            self.main_rail.interpolate(self.main_rail.project(row.geometry))[0], \
                axis=1, result_type = 'expand')
        return points
    
    def _snap_pose(self, pose: Pose) -> Pose:
        pose.coords = self.main_rail.interpolate(self.main_rail.project(pose.coords))[0]
        return pose
    
    @staticmethod
    def _snaped_to_line(points: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """points["geometry"] must be Point typed"""
        line_from_points = LineString(points['geometry'].values)
        lfp_gpd = gpd.GeoDataFrame(geometry = [line_from_points,])
        return lfp_gpd

    def kd_tree(self, radius: float = 0.005):
        idxs = self.points_tree.query_ball_point(x = (self.pose.coords.x,
                                                      self.pose.coords.y), 
                                                 r = radius,
                                                 workers = -1)
        return idxs

    @staticmethod
    def routing(idx, pose_x, pose_y, target_x, target_y, heading) -> Optional[tuple[int, float]]:
        geoid = pyproj.Geod(ellps='WGS84')
        az_front, _, dist = geoid.inv(pose_x, pose_y, target_x, target_y)
        if az_front < 0:
            az_front += 360
        if abs(az_front - heading) < 90:
            return idx, round(dist, 2)

    def data_preapring(self) -> deque:
        closest_points = []
        with ThreadPoolExecutor() as executor:
            result = [executor.submit(self.routing,
                                      idx, 
                                      self.pose.coords.x, 
                                      self.pose.coords.y, 
                                      self.point_base[idx][1].x, 
                                      self.point_base[idx][1].y,
                                      self.pose.heading)
                                      for idx
                                      in self.kd_tree()]
            for f in as_completed(result):
                if f.result() != None:
                    closest_points.append(f.result())
            deq = deque(sorted(closest_points, key=lambda a: a[1]), maxlen=5)
            return deq

    def tracking_info(self) -> None:
        """ Just check closest points info """
        while True:
            route_list = []
            self.pose = self._snap_pose(next(self.emulator))
            route_list.append({"Pose": (round(self.pose.coords.x, 6), \
                                        round(self.pose.coords.y,6)), 
                               "Speed": round(self.pose.velocity, 4),
                               "Heading": round(self.pose.heading, 2)})

            logging.info("Pose: " + " " + str(round(self.pose.coords.x, 6)) + \
                                    " " + str(round(self.pose.coords.y,6)))
            logging.info("Speed: " + " " + str(round(self.pose.velocity, 4)))
            logging.info("Heading: " + " " + str(round(self.pose.heading, 2)))

            for i, dist in self.data_preapring():
                s = {"point_id": self.point_base[i][0], 
                     "point_descript": 1,
                     "point_coord": (round(self.point_base[i][1].x, 6), \
                                     round(self.point_base[i][1].y, 6)), 
                     "direct_m": dist}
                route_list.append(s)
            
            self.shared_memory.clear()
            self.shared_memory.write(route_list)
            print(self.shared_memory)

    def tracking_OSM(self) -> None:
        while True:
            route_list = []
            self.pose = self._snap_pose(next(self.emulator))

            logging.info("Pose: " + " " + str(round(self.pose.coords.x, 6)) + \
                                    " " + str(round(self.pose.coords.y,6)))
            logging.info("Speed: " + " " + str(round(self.pose.velocity, 4)))
            logging.info("Heading: " + " " + str(round(self.pose.heading, 2)))

            with ThreadPoolExecutor(cpu_count()-1) as pool:
                futures = []   
                for i, dist in self.data_preapring():
                    futures.append(pool.submit(self.router.path_builder,
                                               self.pose.coords, 
                                               self.point_base[i][0],
                                               self.point_base[i][1]))

                for f in as_completed(futures):
                    path, length, idx, row = f.result()
                    route_list.append({"point_id": idx,
                                       "point_coord": row, 
                                       "path_osm": self._transformer(path), 
                                       "dist_m": length}) #append route
            for p in route_list:
                print(p)

if __name__ == '__main__':
    nav = Navigator()
    nav.tracking_info()



