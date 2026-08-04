from collections import deque
from analyzers.utils import OscillatorRecord

class OpenInterest:
    def __init__(self, length: int = 200):
        self.length = length
        self.content: deque[OscillatorRecord] = deque(maxlen=length)

    @property
    def current(self):
        return self.content[-1] if self.content else None