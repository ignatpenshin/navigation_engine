version 0.0.2
(Tested on python3.10)

```
New in v.0.0.2:
[1] Moved from KML to GeoJSON. It's simplier and faster to parse.
[2] Intermediate .csv files removed from using
[3] Add DataGrabbler class. It unifies DataFrame build process 
[4] Navigator class refactored from main() to its own utils.navigator.py file
[5] Now we use general classifier based in utils.grabbler.py

Updates in v.0.0.2:
[1] point_base got new structure: [id, geometry, Tag, Description]
[2] rails.get_closest_line(points) ready for active using (updating)
[3] osm_router now in helpers. Just for test some tools/features.
[4] _init_kd_tree got its own method in Navigator()

Open Questions:
[1] How to work with polygons. Tool for fast routing.
[2] How to make OSM_routing faster. Multiprocess optimizations.
[3] Own rail LineString -> MultiDiGraph.
[4] Web map with route streaming.
[5] SharedMemory stability - need tests. 
```

<details><summary>Install:</summary>
<p>

```console
git clone https://github.com/ignatpenshin/navigation_engine.git
cd navigator
pip install -r requirements.txt
```
</p>
</details>

<details><summary>Run:</summary>
<p>

```console
python main.py
```
</p>
</details>

<details><summary>Usage doc:</summary>
<p>

1) main.py will create Navigator class instance and run Navigator.tracking_info()
   it will emulate train-motion data and build kd-tree for 5 closest points:

2) closest points are shared with utils.shared_memory.RamBox object 
   so, you can use it that way:
   
    ```python
    from utils.shared_memory import RamBox
    from time import sleep

    data = RamBox(name = "point_routing", role = "r")

    while True:
        s = data.read()
        if type(s) == list:
            print(s)
            sleep(1)
        continue
    ```
    shared data contains next info (for example):

    ```python
    data: list[dict[str, int|float|str|tuple[float, float]]]
    
    data = [{'Pose': (37.419485, 55.727001), 'Speed': 13.9, 'Heading': 271.27}, 
            {'id': 341, 'coords': (37.415335, 55.726974),'Tag': "path", 'Description': None,  'direct_m': 260.74}, 
            {'id': 696, 'coords': (37.41496, 55.726992), 'Tag': "platform", 'Description': None, 'direct_m': 284.32}, 
            {'id': 697, 'coords': (37.414956, 55.726977),'Tag': "crossing", 'Description': None,  'direct_m': 284.58}, 
            {'id': 117, 'coords': (37.41485, 55.727057), 'Tag': "tongue", 'Description': None, 'direct_m': 291.3}, 
            {'id': 343, 'coords': (37.414614, 55.726994),'Tag': "station", 'Description': "Усово",  'direct_m': 306.06}
           ]
    
                    ### Data Description ###

    # data[0]   -> Train:           Pose (lon, lat: WGS-84), 
    #                               Speed (km/h), 
    #                               Heading (azimuth to North in degrees)

    # data[1:6] -> Point info dict: id (point index from DB), 
    #                               coords (lon, lat: WGS-84)
    #                               Tag (type: str from classifier)
    #                               Description (Optional[str] augmented info)
    #                               direct_m (distance to point in meters)

    ```
3) You can check 
   ```console 
   python test_shared.py 
   ``` 
   to make sure the system is working.

4) By the way: Sometimes there is no detected points around. So you will take only train coords in shared data list. 

</p>
</details>

