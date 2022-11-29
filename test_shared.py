from utils.shared_memory import RamBox
from time import sleep

test = RamBox("point_routing", role = "r")

while True:
    try:
        s = test.read()
        if type(s) == list:
            print(s)
            sleep(1)
        continue
    except Exception as e:
        print(e)
        input()