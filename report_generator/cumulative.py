from global_services.data.provider import DataProvider
from global_services.events.bus import EventBus
from global_services.events.utils import EventBusMsgType
from report_generator.base import BaseReportGenerator


class CumulativeReportGenerator(BaseReportGenerator):
    def __init__(self, report_directory):
        super().__init__(report_directory)
        self.replay_start_time = None

        EventBus().subscribe(EventBusMsgType.PRICE_UPDATE, self._capture_replay_start_time)
        EventBus().subscribe(EventBusMsgType.SESSION_PAIR_END, self.generate_report)

    def _get_current_time(self):
        return DataProvider().get_time()

    def _capture_replay_start_time(self):
        if self.replay_start_time is None:
            self.replay_start_time = self._get_current_time()

    def generate_report(self):
        if self.replay_start_time is None:
            return

        self._render_pdf(
            self.report_directory / "summary.pdf",
            "Summary",
            self._format_time_range(self.replay_start_time),
            self.equity_visualizer,
            self.statistics_visualizer,
        )

    def set_visualizers(self, equity_visualizer, statistics_visualizer):
        self.equity_visualizer = equity_visualizer
        self.statistics_visualizer = statistics_visualizer
        return self