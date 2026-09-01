from abc import ABC, abstractmethod

class MarketEntityVisualizer(ABC):
    """Defines the interface for visualizing market entities."""

    @abstractmethod
    def get_shapes(self):
        """Return the Plotly shapes for the visualization."""
        return []
    
    @abstractmethod
    def get_panel_content(self):
        """Return the panel categories and values for the visualization."""
        return [], [[]]