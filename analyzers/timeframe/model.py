from collections import deque
from analyzers.timeframe.candle import Candle

class Timeframe:
    def __init__(self, length: int, candle_seconds: int):
        self.length = length
        self.candle_seconds = candle_seconds

        self.history: deque[Candle] = deque(maxlen=length - 1)
        self.current: Candle | None = None

    @property
    def content(self):
        if self.current is None:
            return list(self.history)
        return list(self.history) + [self.current]