from data_managers.context.utils import ContextPeriod, ContextCandle

class ContextTimeframe:
    def __init__(self, period: ContextPeriod):
        self.period = period
        self.timeframe = None
        self.content: list[ContextCandle] = []

    @property
    def current(self):
        return self.content[-1] if self.content else None