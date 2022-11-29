import geopandas as gpd
from fiona import drvsupport
import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon

kml_data = r"data/Slam_Ivolga_11-11-2022_14-30-47.kml"

drvsupport.supported_drivers['KML'] = 'r'
df = gpd.read_file(kml_data,  driver='KML')

# Detect
Objs = df[df['geometry'].apply(lambda x : isinstance(x, Point|Polygon))]
Objs.to_csv("objs.csv", sep = ";")
for v in Objs.iterrows():
    print(v)
       
Objs.to_crs(epsg=4326).plot()

fig, ax = plt.subplots(figsize = (50,50))
Objs.to_crs(epsg=4326).plot(ax=ax, color='lightgrey')
Objs.plot(ax=ax, alpha = .1 )
ax.set_title('Objects Ivolga - Belorusky-Usovo')
plt.savefig('Objects_Ivolga')