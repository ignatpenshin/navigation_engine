import geopandas as gpd
import pandas as pd
from typing import Optional
import numpy as np
from shapely.geometry import Point, Polygon, LineString
from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini')
config = config["main"]

class Rails:
    def __init__(self):
        self.rails = config["rails"]
        self._df = self.load_rails()
        self._rail_idx: Optional[np.int64] = None

    @property
    def df(self) -> gpd.GeoDataFrame:
        return self._df
    
    @property
    def rail_idx(self) -> Optional[np.int64]:
        return self._rail_idx
    
    def load_rails(self) -> gpd.GeoDataFrame:
        df = pd.read_csv(self.rails, delimiter=";")
        rails_df = gpd.GeoDataFrame(
            df.loc[:, [c for c in df.columns \
            if c != "geometry" and c != "Unnamed: 0"]],
            geometry=gpd.GeoSeries.from_wkt(df["geometry"]))
        del df
        return rails_df
    
    def get_closest_line(self, point: Point) -> gpd.GeoDataFrame:
        self._rail_idx: Optional[np.int64] = self._df.distance(point).sort_values().index[0]
        closest_line = self._df.iloc[[self._rail_idx]]
        return closest_line
    
    def create_buffer(self, width: float = 0.005) -> Polygon:
        buf_polygon = self._df.iloc[[self._rail_idx]].buffer(width)
        return buf_polygon