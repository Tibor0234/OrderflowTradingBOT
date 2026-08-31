from abc import ABC, abstractmethod

class PriceChartVisualizer(ABC):
    is_oscillator = False
    uses_volume_axis = False

    def __init__(self, chart_slot: int = 0):
        self.chart_slot = chart_slot

    def get_traces(self):
        return []

    def get_shapes(self):
        return []