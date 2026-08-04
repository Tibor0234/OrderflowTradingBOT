from collections import deque
from analyzers.utils import OscillatorRecord

class OrderBookImbalance:
    def __init__(self, depth: int = 20, length: int = 10):
        self.depth = depth
        self.length = length
        self.content: deque[OscillatorRecord] = deque(maxlen=length)

    @property
    def current(self):
        return self.content[-1] if self.content else None