from abc import ABC, abstractmethod
from data_managers.context.utils import ContextPeriod

class ContextChartVisualizer(ABC):
    def __init__(self):
        self.period: ContextPeriod

    def get_traces(self):
        return []
    
    def get_shapes(self):
        return []