import plotly.graph_objects as go
from datetime import datetime, timedelta
from visualizers.context_chart.base import ContextChartVisualizer
from analyzers.ohlcv_volume_profile.model import OHLCVVolumeProfile

class OHLCVVolumeProfileVisualizer(ContextChartVisualizer):
    def __init__(self, volume_profile: OHLCVVolumeProfile):
        self.volume_profile = volume_profile
        self.period = self.volume_profile.period

        self.bar = go.Bar(
            x=[],
            y=[],
            orientation="h",
            name=f"VP",
            marker=dict(color="rgba(0, 0, 255, 0.5)"),
            showlegend=False
        )

    def get_traces(self):
        bins = self.volume_profile.content

        start_dt = datetime.fromtimestamp(self.volume_profile.start_time / 1000)

        self.bar.x = [start_dt + timedelta(seconds=float(b.volume)) for b in bins]
        self.bar.y = [b.low + b.size / 2 for b in bins]

        return self.bar

    def get_shapes(self):
        shapes = []

        poc_price = self.volume_profile.poc.price
        if poc_price is not None:
            shapes.append(
                dict(
                    type="line",
                    xref="paper",
                    x0=0,
                    x1=1,
                    yref="y",
                    y0=poc_price,
                    y1=poc_price,
                    line=dict(color="yellow", width=1, dash="dash")
                )
            )

        value_area = self.volume_profile.value_area
        if value_area.high is not None and value_area.low is not None:
            shapes.append(
                dict(
                    type="rect",
                    xref="paper",
                    yref="y",
                    x0=0,
                    x1=1,
                    y0=value_area.low,
                    y1=value_area.high,
                    fillcolor="rgba(0, 0, 255, 0.1)",
                    line=dict(width=0),
                )
            )
            shapes.append(
                dict(
                    type="line",
                    xref="paper",
                    yref="y",
                    x0=0,
                    x1=1,
                    y0=value_area.low,
                    y1=value_area.low,
                    line=dict(color="rgba(0, 0, 255, 0.5)", width=1),
                )
            )
            shapes.append(
                dict(
                    type="line",
                    xref="paper",
                    yref="y",
                    x0=0,
                    x1=1,
                    y0=value_area.high,
                    y1=value_area.high,
                    line=dict(color="rgba(0, 0, 255, 0.5)", width=1),
                )
            )

        return shapes