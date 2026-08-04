from collections import deque
from decimal import Decimal

class BigTradesAnalyzer:
    def __init__(self, length, top_pct=10):
        self.length = length
        self.top_rate = Decimal(top_pct / 100)

        self.max_trades_window: deque[Decimal] = deque(maxlen=length)
        self.current_candle_max = Decimal(0)

    def override(self, length, top_pct):
        if length is not None:
            self.length = length
            self.max_trades_window = deque(maxlen=length)
        if top_pct is not None:
            self.top_rate = Decimal(top_pct / 100)

    def reset(self):
        self.max_trades_window.clear()
        self.current_candle_max = Decimal(0)

    def update_record(self, quantity):
        if quantity > self.current_candle_max:
            self.current_candle_max = quantity

    def close_record(self):
        self.max_trades_window.append(self.current_candle_max)
        self.current_candle_max = Decimal(0)

    def is_big_trade(self, quantity):
        if not self.max_trades_window:
            return False

        avg_max = (sum(self.max_trades_window)) / len(self.max_trades_window)
        threshold = avg_max * (1 - self.top_rate)

        return quantity >= threshold