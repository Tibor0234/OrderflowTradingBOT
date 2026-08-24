import time
from visualizers.data_analysis.equity_curve import EquityCurveVisualizer
from visualizers.data_analysis.statistics import StatisticsVisualizer
from global_services.events.bus import EventBus
from global_services.events.utils import EventBusMsgType


class ReportGenerator:
    def __init__(self, strategy_name):
        self.strategy_name = strategy_name

        self.started_at = time.time()

        EventBus().subscribe(EventBusMsgType.SESSION_END, self.generate_session_report)
        EventBus().subscribe(EventBusMsgType.PROCESS_END, self.generate_backtest_summary)

    def generate_session_report(self):
        pass

    def generate_backtest_summary(self):
        pass

    def set_equity_curve_visualizers(self, session_visualizer: EquityCurveVisualizer, cumulative_visualizer: EquityCurveVisualizer):
        self.session_equity_visualizer = session_visualizer
        self.cumulative_equity_visualizer = cumulative_visualizer
        return self
    
    def set_statistics_visualizers(self, session_visualizer: StatisticsVisualizer, cumulative_visualizer: StatisticsVisualizer):
        self.session_statistics_visualizer = session_visualizer
        self.cumulative_statistics_visualizer = cumulative_visualizer
        return self