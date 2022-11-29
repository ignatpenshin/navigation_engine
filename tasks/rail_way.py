import geopandas as gpd
from fiona import drvsupport
import matplotlib.pyplot as plt
from shapely.geometry import LineString

kml_data = r"data/Slam_Ivolga_11-11-2022_14-30-47.kml"

drvsupport.supported_drivers['KML'] = 'r'
df = gpd.read_file(kml_data,  driver='KML')

# RailWays
rail_df = df[df['geometry'].apply(lambda x : isinstance(x, LineString))]
rail_df.to_csv("rails.csv", sep = ";")
for v in rail_df.iterrows():
    print(v)
       
rail_df.to_crs(epsg=4326).plot()

fig, ax = plt.subplots(figsize = (50,50))
rail_df.to_crs(epsg=4326).plot(ax=ax, color='lightgrey')
rail_df.plot(ax=ax, alpha = .1 )
ax.set_title('RailWay Ivolga - Belorusky-Usovo')
plt.savefig('Railway_Ivolga')