import geopandas as gpd
import pandas as pd
from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini')
config = config["main"]

class Objects:
    def __init__(self):
        self.objs = config["objs"]
        self._df = self.load_objs()

    @property
    def df(self) -> gpd.GeoDataFrame:
        return self._df
    
    def load_objs(self) -> gpd.GeoDataFrame:
        df = pd.read_csv(self.objs, delimiter=";")
        objs_df = gpd.GeoDataFrame(
            df.loc[:, [c for c in df.columns \
            if c != "geometry" and c != "Unnamed: 0"]], crs = 4326,
            geometry=gpd.GeoSeries.from_wkt(df["geometry"]))
        del df
        return objs_df

    def get_Points(self) -> gpd.GeoDataFrame:
        return self._df[self._df.geom_type=="Point"]
    
    def get_Polygons(self) -> gpd.GeoDataFrame:
        return self._df[self._df.geom_type=="Polygon"]