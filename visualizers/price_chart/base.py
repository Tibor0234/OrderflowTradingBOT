from abc import ABC, abstractmethod

class PriceChartVisualizer(ABC):
    def get_traces(self):
        return []

    def get_shapes(self):
        return []