import dash
from dash import Input, Output
from dashboard.chart_renderer import ChartRenderer
from dashboard.dashboard_layout import DashboardLayout
from dashboard.panel_content_renderer import PanelContentRenderer
from data_managers.context.utils import ContextPeriod
from visualizers.price_chart.base import PriceChartVisualizer
from visualizers.context_chart.base import ContextChartVisualizer
from visualizers.market_entity.trade import TradeVisualizer
from visualizers.market_entity.order import OrderVisualizer
from visualizers.data_analysis.statistics import StatisticsVisualizer
from visualizers.data_analysis.equity_curve import EquityCurveVisualizer
from market_feed.utils import SessionCounter
from dashboard.session_report import SessionReport, SessionReportSnapshot

class LiveDashboard:
    def __init__(self, title):

        self.app = dash.Dash(__name__)
        self.app.title = title

        self.layout = DashboardLayout()
        self.chart_renderer = ChartRenderer()
        self.panel_content_renderer = PanelContentRenderer()

        self.price_visualizers = []
        self.context_visualizers = {
            ContextPeriod.LAST_DAY: [],
            ContextPeriod.LAST_WEEK: []
        }

        self.trade_visualizer = None
        self.order_visualizer = None

        self.session_counter = None

        self.session_equity_visualizer = None
        self.cumulative_equity_visualizer = None

        self.session_statistics_visualizer = None
        self.cumulative_statistics_visualizer = None

        self.app.layout = self.layout.build()

        self.session_report = SessionReport(self._build_report_snapshot)
        self._register_callbacks()

    def _build_dashboard_snapshot(self):
        figures = {
            "Price chart": self.chart_renderer.build_price_chart(
                [self.trade_visualizer, self.order_visualizer],
                self.price_visualizers
            ),
            "Last week chart": self.chart_renderer.build_context_chart(
                self.context_visualizers[ContextPeriod.LAST_WEEK]
            ),
            "Last day chart": self.chart_renderer.build_context_chart(
                self.context_visualizers[ContextPeriod.LAST_DAY]
            ),
            "Session equity curve": self.chart_renderer.build_equity_curve(
                self.session_equity_visualizer
            ),
            "Cumulative equity curve": self.chart_renderer.build_equity_curve(
                self.cumulative_equity_visualizer
            )
        }

        panels = {
            "Session": self.panel_content_renderer.render_session_panel(
                self.session_counter
            ),
            "Trades": self.panel_content_renderer.render_execution_panel(
                self.trade_visualizer
            ),
            "Orders": self.panel_content_renderer.render_execution_panel(
                self.order_visualizer
            ),
            "Session statistics": self.panel_content_renderer.render_stats_panel(
                self.session_statistics_visualizer
            ),
            "Cumulative statistics": self.panel_content_renderer.render_stats_panel(
                self.cumulative_statistics_visualizer
            )
        }

        session_number = None
        if self.session_counter:
            session_number = self.session_counter.current

        return SessionReportSnapshot(session_number, figures, panels)

    def _build_report_snapshot(self):
        snapshot = self._build_dashboard_snapshot()
        return SessionReportSnapshot(
            session_number=snapshot.session_number,
            figures={
                "Session equity curve": snapshot.figures["Session equity curve"],
                "Cumulative equity curve": snapshot.figures["Cumulative equity curve"]
            },
            panels={
                "Session": snapshot.panels["Session"],
                "Session statistics": snapshot.panels["Session statistics"],
                "Cumulative statistics": snapshot.panels["Cumulative statistics"]
            }
        )

    def _register_callbacks(self):

        @self.app.callback(
            Output("price-chart", "figure"),
            Output("last-week-chart", "figure"),
            Output("last-day-chart", "figure"),
            Output("session-equity-curve", "figure"),
            Output("cumulative-equity-curve", "figure"),
            Output("session-panel", "children"),
            Output("trade-panel", "children"),
            Output("order-panel", "children"),
            Output("session-stats-panel", "children"),
            Output("cumulative-stats-panel", "children"),
            Input("trigger-check", "n_intervals")
        )
        def update(_):
            snapshot = self._build_dashboard_snapshot()
            return (*snapshot.figures.values(), *snapshot.panels.values())

    def add_price_chart_visualizer(self, visualizer: PriceChartVisualizer):
        self.price_visualizers.append(visualizer)
        return self

    def add_context_chart_visualizer(self, visualizer: ContextChartVisualizer):
        self.context_visualizers[visualizer.period].append(visualizer)
        return self
    
    def set_session_counter(self, session_counter: SessionCounter):
        self.session_counter = session_counter
        return self

    def set_execution_visualizers(self, trade_visualizer: TradeVisualizer, order_visualizer: OrderVisualizer):
        self.trade_visualizer = trade_visualizer
        self.order_visualizer = order_visualizer
        return self

    def set_equity_curve_visualizers(self, session_visualizer: EquityCurveVisualizer, cumulative_visualizer: EquityCurveVisualizer):
        self.session_equity_visualizer = session_visualizer
        self.cumulative_equity_visualizer = cumulative_visualizer
        return self
    
    def set_statistics_visualizers(self, session_visualizer: StatisticsVisualizer, cumulative_visualizer: StatisticsVisualizer):
        self.session_statistics_visualizer = session_visualizer
        self.cumulative_statistics_visualizer = cumulative_visualizer
        return self

    def run(self, debug=True):
        self.app.run(debug=debug)