import geopandas as gpd
from utils.grabbler import DataGrabbler

class Objects:
    def __init__(self):
        datagrabbler = DataGrabbler()
        self._df = datagrabbler.gpd_general

    @property
    def df(self) -> gpd.GeoDataFrame:
        return self._df

    def get_Points(self) -> gpd.GeoDataFrame:
        return self._df[self._df.geom_type=="Point"]
    
    def get_Polygons(self) -> gpd.GeoDataFrame:
        return self._df[self._df.geom_type=="Polygon"]
    
    def get_LineStrings(self) -> gpd.GeoDataFrame:
        return self._df[self._df.geom_type=="LineString"]