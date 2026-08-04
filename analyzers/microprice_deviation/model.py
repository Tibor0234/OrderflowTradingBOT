from collections import deque
from analyzers.utils import OscillatorRecord

class MicropriceDeviation:
    def __init__(self, length: int = 10):
        self.length = length
        self.content: deque[OscillatorRecord] = deque(maxlen=length)

    @property
    def current(self):
        return self.content[-1] if self.content else None