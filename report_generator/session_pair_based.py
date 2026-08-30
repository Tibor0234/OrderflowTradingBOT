from global_services.data.provider import DataProvider
from global_services.events.bus import EventBus
from global_services.events.utils import EventBusMsgType
from report_generator.base import BaseReportGenerator


class SessionPairBasedReportGenerator(BaseReportGenerator):
    def __init__(self, report_directory):
        super().__init__(report_directory)
        self.session_pair_start_time = None

        EventBus().subscribe(EventBusMsgType.SESSION_PAIR_START, self._reset_session_pair_start_time)
        EventBus().subscribe(EventBusMsgType.PRICE_UPDATE, self._capture_session_pair_start_time)
        EventBus().subscribe(EventBusMsgType.SESSION_PAIR_END, self.generate_report)

    def _get_current_time(self):
        return DataProvider().get_time()

    def _reset_session_pair_start_time(self):
        self.session_pair_start_time = None

    def _capture_session_pair_start_time(self):
        if self.session_pair_start_time is None:
            self.session_pair_start_time = self._get_current_time()

    def generate_report(self):
        symbol = DataProvider().get_symbol()
        session_number = self.session_counter.session
        report_path = self.report_directory / f"session_{session_number}-{symbol}.pdf"
        self._render_pdf(
            report_path,
            f"Session {session_number} - {symbol}",
            self._format_time_range(self.session_pair_start_time),
            self.equity_visualizer,
            self.statistics_visualizer,
        )

    def set_session_counter(self, session_counter):
        self.session_counter = session_counter
        return self

    def set_visualizers(self, equity_visualizer, statistics_visualizer):
        self.equity_visualizer = equity_visualizer
        self.statistics_visualizer = statistics_visualizer
        return self