import json
import os
import logging
from typing import Optional, Any
from configparser import ConfigParser

import geopandas as gpd 
from shapely.geometry import Point, LineString, Polygon

config = ConfigParser()
config.read('config.ini')
config = config["main"]

class DataGrabbler:
    def __init__(self):
        self.geojson_file = os.path.join(config["path_data"], config["geojson"])
        self.classifier = {(LineString, "#ed4543"): "path",
                           (Polygon, "#ffd21e"): "platform", 
                           (Polygon, "#56db40"): "crossing",
                           (Point, "#1bad03"): "traffic_light",
                           (Point, "#ffd21e"): "frog",
                           (Point, "#b51eff"): "tongue",
                           (Point, "#1e98ff"): "station"}

        self.general: dict = self._init_general()
        self._geojson_parser()
        self._gpd_general = gpd.GeoDataFrame(self.general, crs = "epsg:4326")
        logging.info("GeoJSON data -> GeoDataFrame: Done")

    @staticmethod
    def _init_general() -> dict: 
        general = {"id": list(), 
                   "Tag": list(), 
                   "Description": list(), 
                   "geometry": list()}
        return general

    def _append_data(self, id: int, tag: str, \
                     descript: Optional[str], coords: Point|LineString|Polygon):

        self.general["id"].append(id)
        self.general["Tag"].append(tag)
        self.general["Description"].append(descript)
        self.general["geometry"].append(coords)

    def _geojson_parser(self) -> None:
        with open(self.geojson_file, encoding='utf8') as f:
            d = json.load(f) 
            for part in d['features']:
                if part["geometry"]["type"] == "Point":
                    id = part["id"]
                    color = part["properties"]["marker-color"]
                    coords = Point(part["geometry"]["coordinates"])
                    tag = self.classifier[(Point, color)]
                    try:
                        descript = part["properties"]["description"]
                    except KeyError:
                        descript = None
                    self._append_data(id, tag, descript, coords)

                if part["geometry"]["type"] == "LineString":
                    id = part["id"] 
                    color = part["properties"]["stroke"]
                    coords = LineString(part["geometry"]["coordinates"])
                    tag = self.classifier[(LineString, color)]
                    try:
                        descript = part["properties"]["description"]
                    except KeyError:
                        descript = None
                    self._append_data(id, tag, descript, coords)

                if part["geometry"]["type"] == "Polygon":
                    id = part["id"] 
                    color = part["properties"]["fill"]
                    coords = Polygon(part["geometry"]["coordinates"][0])
                    tag = self.classifier[(Polygon, color)]
                    try:
                        descript = part["properties"]["description"]
                    except KeyError:
                        descript = None
                    self._append_data(id, tag, descript, coords)

    @property
    def gpd_general(self):
        return self._gpd_general
    
    @gpd_general.setter
    def gpd_general(self, val: Any):
        pass

    def save_obj(self):
        self._gpd_general.to_csv(os.path.join(config["path_pandas_data"], "objs.csv"), sep = ";")


