from data_managers.ohlcv.utils import OHLCVPeriod, OHLCVCandle

class OHLCVTimeframe:
    def __init__(self, period: OHLCVPeriod):
        self.period = period
        self.timeframe = None
        self.content: list[OHLCVCandle] = []

    @property
    def current(self):
        return self.content[-1] if self.content else None