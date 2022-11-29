from shapely.geometry import Point

class Pose:
    def __init__(self, data: dict):
        self._coords: Point = Point(*data["coords"])
        self._heading: float = data["heading"]
        self._velocity: float = data["velocity"]

    @property
    def velocity(self) -> float:
        return self._velocity
    
    @velocity.setter
    def velocity(self, value):
        pass
    
    @property
    def coords(self) -> Point:
        return self._coords

    @coords.setter
    def coords(self, point: Point) -> None:
        self._coords = point
    
    @property
    def heading(self) -> float:
        return self._heading
    
    @heading.setter
    def heading(self, val) -> None:
        pass