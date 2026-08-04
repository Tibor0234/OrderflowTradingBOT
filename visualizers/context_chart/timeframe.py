from datetime import datetime
import plotly.graph_objects as go
from analyzers.context_timeframe.model import ContextTimeframe
from visualizers.context_chart.base import ContextChartVisualizer

class ContextTimeframeVisualizer(ContextChartVisualizer):
    def __init__(self, timeframe: ContextTimeframe):
        self.timeframe = timeframe
        self.period = timeframe.period

        self.candlestick = self.candlestick = go.Candlestick(
            x=[],
            open=[],
            high=[],
            low=[],
            close=[],
            showlegend=False
        )

    def get_traces(self):
        candles = self.timeframe.content

        if not candles: return []

        self.candlestick.x = [datetime.fromtimestamp(c.time / 1000) for c in candles]
        self.candlestick.open = [c.open for c in candles]
        self.candlestick.high = [c.high for c in candles]
        self.candlestick.low = [c.low for c in candles]
        self.candlestick.close = [c.close for c in candles]

        return self.candlestick