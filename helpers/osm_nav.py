import pandas as pd
import geopandas as gpd
from shapely.geometry import LineString, Point
import osmnx  as ox
import networkx as nx
import matplotlib.pyplot as plt


north_west = [55.791226, 37.191971]
south_east = [55.721652, 37.606126]

pose = [37.577770, 55.775922]
finish = [37.207905, 55.729025]

#Pose
pose_gdf = gpd.GeoDataFrame(columns = ["name","geometry"], crs = 4326, geometry = "geometry")
pose_gdf.at[0, "geometry"] = Point(*pose)
pose_gdf.at[0, "name"] = "Pose"
#Finish
finish_gdf = gpd.GeoDataFrame(columns = ["name","geometry"], crs = 4326, geometry = "geometry")
finish_gdf.at[0, "geometry"] = Point(*finish)
finish_gdf.at[0, "name"] = "Finish"

utw = ox.settings.useful_tags_way + ['railway']
ox.settings.log_console=True 
ox.settings.use_cache=True 
ox.settings.useful_tags_way=utw

G = ox.graph_from_bbox(north = north_west[0], 
                       south = south_east[0],
                       east = south_east[1], 
                       west = north_west[1],
                       simplify= False,  
                       custom_filter = '["railway"]'
)


fig, ax = ox.plot_graph(G, node_size=2, node_color='r', edge_color='w', edge_linewidth=0.2)

graph_proj = ox.project_graph(G)

edges = ox.graph_to_gdfs(graph_proj, nodes=False) 

#edges = edges.to_crs("epsg:4326") 
CRS = edges.crs
pose_proj=pose_gdf.to_crs(crs=CRS) 
finish_proj=finish_gdf.to_crs(crs=CRS)

routes = gpd.GeoDataFrame()

nodes = ox.graph_to_gdfs(graph_proj, edges=False)


for oidx, orig in pose_proj.iterrows():
    print("pose_proj data: ", oidx, orig)
    closest_origin_node = ox.nearest_nodes(G=graph_proj, Y=orig.geometry.y, X=orig.geometry.x) #, method="euclidean")
    for tidx, target in finish_proj.iterrows():
        print("pose_proj data: ", tidx, target)
        closest_target_node = ox.nearest_nodes(G=graph_proj, X=target.geometry.x, Y=target.geometry.y) #, method="euclidean")
        if closest_origin_node == closest_target_node:
            continue

route = nx.shortest_path(graph_proj, source=closest_origin_node, target=closest_target_node, weight="length")
route_nodes = nodes.loc[route]
path = LineString(list(route_nodes.geometry.values))
print(path.length)
path_gpd = gpd.GeoDataFrame(geometry = [path,])

path_gpd.plot()
plt.show()



