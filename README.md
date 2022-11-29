version 0.0.1

<details><summary>Install:</summary>
<p>

```console
git clone https://bitbucket.locotech-signal.ru/scm/~ignat.penshin/navigator.git
chdir navigator
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
            {'point_id': 341, 'point_descript': 1, 'point_coord': (37.415335, 55.726974), 'direct_m': 260.74}, 
            {'point_id': 696, 'point_descript': 1, 'point_coord': (37.41496, 55.726992), 'direct_m': 284.32}, 
            {'point_id': 697, 'point_descript': 1, 'point_coord': (37.414956, 55.726977), 'direct_m': 284.58}, 
            {'point_id': 117, 'point_descript': 1, 'point_coord': (37.41485, 55.727057), 'direct_m': 291.3}, 
            {'point_id': 343, 'point_descript': 1, 'point_coord': (37.414614, 55.726994), 'direct_m': 306.06}
           ]
    
                    ### Data Description ###

    # data[0]   -> Train:           Pose (lon, lat: WGS-84), 
    #                               Speed (km/h), 
    #                               Heading (azimuth to North in degrees)

    # data[1:6] -> Point info dict: point_id (point index from DB), 
    #                               point_descript (type/color/style/word, e.g. any classifier)
    #                               point_coord (lon, lat: WGS-84)
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

