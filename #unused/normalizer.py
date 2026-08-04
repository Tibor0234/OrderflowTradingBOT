from collections import deque
from sessions.session_based_object import SessionBasedObject
from decimal import Decimal

class Normalizer(SessionBasedObject):
    def __init__(self, range, length=14):
        self.length = length
        self.range = range

        self.real_values_window: deque[Decimal] = deque(maxlen=length)

    def override(self, length=None):
        if length is not None:
            self.length = length
            self.real_values_window = deque(maxlen=length)

    def reset(self):
        self.real_values_window.clear()

    def get_value(self, value: Decimal):
        if not self.real_values_window:
            return (self.range[1] - self.range[0]) / 2

        min_val = min(self.real_values_window)
        max_val = max(self.real_values_window)

        if max_val == min_val:
            return (self.range[1] - self.range[0]) / 2

        norm = (value - min_val) / (max_val - min_val)
        norm = max(range[0], min(range[1], norm))

        return self.range[0] + norm * (self.range[1] - self.range[0])

    def close_record(self, value: Decimal):
        self.real_values_window.append(value)