from analyzers.volume_delta.base_analyzer import BaseVolumeDeltaAnalyzer
from analyzers.utils import OscillatorRecord

class CVDAnalyzer(BaseVolumeDeltaAnalyzer):
    def __init__(self, big_trades=False, visualize=True):
        super().__init__(big_trades, visualize)

    def get_visualizer(self):
        if self.visualize:
            from visualizers.price_chart.cvd import CVDVisualizer
            return CVDVisualizer(self.model)
        return None

    def new_current_record(self, next_time=None):
        return OscillatorRecord(
            time=next_time if next_time is not None else self.model.current.time,
            value=self.model.current.value
        )