from abc import ABC, abstractmethod

class MarketEntityVisualizer(ABC):
    @abstractmethod
    def get_shapes(self):
        return []
    
    @abstractmethod
    def get_panel_content(self):
        return [], [[]]