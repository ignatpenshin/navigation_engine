from multiprocessing.shared_memory import SharedMemory
import pickle

class RamBox:
    
    def __str__(self):
        return str(self.read())
    
    def _initialWrite(self):
        self.write(0)
        
    def clear(self):
        self._initialWrite()

    def __init__(self, name: str, role="r", size=10000000):
        self._name = name
        self._role = role
        self._size = size
        if role == "w":
            self._memory = SharedMemory(name=name, create=True, size=size)
            self._initialWrite()
        elif role == "r":
            self._memory = SharedMemory(name=name)
        else:
            raise RuntimeError("role must be 'r' or 'w' got "+str(role))

    def __del__(self):
        self._memory.close()
        self._memory.unlink()

    def read(self):
        lencell = 8
        buffer = self._memory.buf
        blen = buffer[0:lencell]
        length = int.from_bytes(blen, byteorder="little", signed=False)
        bdata = buffer[lencell:length+lencell]
        data = pickle.loads(bdata)
        return data

    def write(self, data):
        bdata = pickle.dumps(data)
        dlen = len(bdata)
        blen = dlen.to_bytes(length=8, byteorder="little", signed=False)
        pack = blen+bdata
        self._memory.buf[:len(pack)] = pack