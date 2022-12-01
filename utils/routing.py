import geopandas as gpd
from shapely.geometry import LineString, Point
import osmnx  as ox
import networkx as nx
import logging
import matplotlib.pyplot as plt


class Routing:
    """
    Belorussky - Usovo polygon
    """
    def __init__(self, pose: Point): #, rail: gpd.GeoDataFrame): 
        self.north_west = [55.791226, 37.191971]
        self.south_east = [55.721652, 37.606126]

        self._utw = ox.settings.useful_tags_way + ['railway']
        ox.settings.log_console=False
        ox.settings.use_cache=True 
        ox.settings.useful_tags_way=self._utw

        self._pose_gdf = self._pose_init(pose)

        self.points = gpd.GeoDataFrame(columns = ["name", "geometry"], 
                   crs = 4326, 
                   geometry = "geometry")
        
        self.G = ox.graph_from_bbox(north = self.north_west[0], 
                               south = self.south_east[0],
                               east = self.south_east[1], 
                               west = self.north_west[1],
                               simplify= False,  
                               custom_filter = '["railway"]'
        )
        logging.info(f"OSM {self.G}: inited")

        self.graph_proj = ox.project_graph(self.G) #web-merkator 'EPSG:3857'
        self.edges = ox.graph_to_gdfs(self.graph_proj, nodes=False) 
        self.nodes = ox.graph_to_gdfs(self.graph_proj, edges=False)
        self.CRS = self.edges.crs

    def _pose_init(self, pose: Point):
        pose_gdf = gpd.GeoDataFrame(columns = ["name","geometry"], crs = 4326, geometry = "geometry")
        pose_gdf.at[0, "geometry"] = pose
        pose_gdf.at[0, "name"] = "Pose"
        return pose_gdf

    def path_builder(self, pose: Point, idx: int, row: Point) -> tuple[LineString, float, int, Point]:
        self.points.at[0, "geometry"] = row
        self.points.at[0, "name"] = idx
        self._pose_gdf.at[0, "geometry"] = pose

        pose_proj = self._pose_gdf.to_crs(crs=self.CRS) 
        finish_proj = self.points.to_crs(crs=self.CRS)
        for oidx, orig in pose_proj.iterrows():
            closest_origin_node = ox.nearest_nodes(G=self.graph_proj, Y=orig.geometry.y, X=orig.geometry.x)
            for tidx, target in finish_proj.iterrows():
                closest_target_node = ox.nearest_nodes(G=self.graph_proj, X=target.geometry.x, Y=target.geometry.y)
                if closest_origin_node == closest_target_node:
                    continue
                
        route = nx.shortest_path(self.graph_proj, source=closest_origin_node, target=closest_target_node, weight="length")
        route_nodes = self.nodes.loc[route]
        path = LineString(list(route_nodes.geometry.values))
        return path, round(path.length,2), idx, row            
        







