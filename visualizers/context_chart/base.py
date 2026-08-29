from abc import ABC, abstractmethod
from data_managers.ohlcv.utils import OHLCVPeriod

class ContextChartVisualizer(ABC):
    def __init__(self):
        self.period: OHLCVPeriod

    def get_traces(self):
        return []
    
    def get_shapes(self):
        return []