import plotly.graph_objects as go
from visualizers.price_chart.base import PriceChartVisualizer
from analyzers.volume_delta.model import VolumeDelta

class VolumeDeltaVisualizer(PriceChartVisualizer):
    def __init__(
        self,
        volume_delta_analyzer: VolumeDelta,
        big_trades_top_pct: float | None = None,
    ):
        self.volume_delta_analyzer = volume_delta_analyzer

        name = "VD"
        if big_trades_top_pct is not None:
            name += f" (Big Trades {big_trades_top_pct:g}%)"

        self.bar = go.Bar(
            x=[],
            y=[],
            name=name,
            yaxis="y2",
        )

    def get_traces(self):
        combined = list(self.volume_delta_analyzer.content)

        x_vals = [r.time for r in combined]
        y_vals = [float(r.value) for r in combined]

        colors = [
            "rgba(0, 153, 76, 1)" if y >= 0 else "rgba(200, 39, 40, 1)"
            for y in y_vals
        ]

        self.bar.x = x_vals
        self.bar.y = y_vals
        self.bar.marker = dict(color=colors)

        return self.bar