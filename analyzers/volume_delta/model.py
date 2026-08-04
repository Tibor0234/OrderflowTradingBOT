from collections import deque
from analyzers.utils import OscillatorRecord

class VolumeDelta:
    def __init__(self, length: int):
        self.length = length

        self.history: deque[OscillatorRecord] = deque(maxlen=length)
        self.current: OscillatorRecord | None = None

    @property
    def content(self):
        if self.current is None:
            return list(self.history)
        return list(self.history) + [self.current]