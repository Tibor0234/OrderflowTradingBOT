from visualizer.price_chart_visualizer import PriceChartVisualizer
from model.tickframe import Tickframe
import plotly.graph_objects as go
from datetime import datetime

class TickframeVisualizer(PriceChartVisualizer):
    def __init__(self, tickframe: Tickframe):
        self.tickframe = tickframe

    def get_traces(self):
        candles = list(self.tickframe.content)
        if self.tickframe.current_candle is not None and self.tickframe.current_candle.open is not None:
            candles.append(self.tickframe.current_candle)

        if not candles: return []
        
        return go.Candlestick(
            #x=x_times,
            open=[c.open for c in candles],
            high=[c.high for c in candles],
            low=[c.low for c in candles],
            close=[c.close for c in candles],
            name=f'{self.tickframe.symbol} {self.tickframe.tick_rate}t'
       )