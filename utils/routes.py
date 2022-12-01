import geopandas as gpd
import pandas as pd
from typing import Optional
import numpy as np
import logging
from shapely.geometry import Point, Polygon, LineString


class Rails:
    def __init__(self, df: gpd.GeoDataFrame):
        self._df = df
        self._rail_idx: Optional[np.int64] = None

    @property
    def df(self) -> gpd.GeoDataFrame:
        return self._df
    
    @property
    def rail_idx(self) -> Optional[np.int64]:
        return self._rail_idx
    
    def get_closest_line(self, point: Point) -> gpd.GeoDataFrame:
        self._rail_idx: Optional[np.int64] = self._df.distance(point).sort_values().index[0]
        closest_line = self._df.loc[self._df["id"] == self._rail_idx]
        logging.info(f"Closest rail-path with id = {self._rail_idx}: inited")
        return closest_line
    
    def create_buffer(self, width: float = 0.005) -> Polygon:
        buf_polygon = self._df.iloc[[self._rail_idx]].buffer(width)
        return buf_polygon