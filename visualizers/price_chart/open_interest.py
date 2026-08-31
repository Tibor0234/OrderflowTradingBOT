import plotly.graph_objects as go
from visualizers.price_chart.base import PriceChartVisualizer
from analyzers.open_interest.model import OpenInterest

class OpenInterestVisualizer(PriceChartVisualizer):
    def __init__(self, open_interest_analyzer: OpenInterest, aggregation_minutes: int):
        self.open_interest_analyzer = open_interest_analyzer

        self.scatter = go.Scattergl(
            x=[],
            y=[],
            mode="lines",
            name=f"OI ({aggregation_minutes}m)",
            yaxis="y2",
            line=dict(color="rgba(52, 152, 219, 1)", width=1),
        )

    def get_traces(self):
        combined = list(self.open_interest_analyzer.content)

        self.scatter.x = [r.time for r in combined]
        self.scatter.y = [float(r.value) for r in combined]

        return self.scatter