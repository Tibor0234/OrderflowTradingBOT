class Candle:
    def __init__(self, time, open):
        self.time = time
        self.open = open
        self.high = open
        self.low = open
        self.close = open

    def update_candle(self, price):
        self.high = max(self.high, price)
        self.low = min(self.low, price)
        self.close = price