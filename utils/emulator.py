import time
import json
from .pose import Pose
from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini')
config = config["main"]

class Emulator:
    def __init__(self, freq: int):
        self._track = open(config["emulation"], "r")
        self.freq = freq
        self.data = None

    @property
    def track(self):
        pass

    def __iter__(self):
        return self
    
    def __next__(self) -> dict:
        line = self._track.readline()
        while line == "\n":
            line = self._track.readline()
            if not line:
                self._track.close()
                raise StopIteration
        line = "{" + \
            line.replace("data", "\"data\"") + "}"
        self.data = json.loads(line)["data"]
        time.sleep(self.freq)
        return Pose(self.data)