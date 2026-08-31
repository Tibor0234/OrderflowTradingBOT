from analyzers.volume_delta.base_analyzer import BaseVolumeDeltaAnalyzer
from analyzers.big_trades.analyzer import BigTradesAnalyzer
from analyzers.utils import OscillatorRecord
from decimal import Decimal

class VolumeDeltaAnalyzer(BaseVolumeDeltaAnalyzer):
    def __init__(self, big_trades: BigTradesAnalyzer | None = None, visualize=True):
        super().__init__(big_trades, visualize)

    def get_visualizer(self):
        if self.visualize:
            from visualizers.price_chart.volume_delta import VolumeDeltaVisualizer
            top_pct = (
                self.big_trades_analyzer.top_pct
                if self.big_trades_analyzer is not None
                else None
            )
            return VolumeDeltaVisualizer(self.model, top_pct)
        return None

    def new_current_record(self, next_time=None):
        return OscillatorRecord(
            time=next_time if next_time is not None else 0,
            value=Decimal(0)
        )