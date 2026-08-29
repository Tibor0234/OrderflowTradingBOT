import time
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from market_feed.utils import SessionCounter
from visualizers.data_analysis.equity_curve import EquityCurveVisualizer
from visualizers.data_analysis.statistics import StatisticsVisualizer
from global_services.events.bus import EventBus
from global_services.events.utils import EventBusMsgType
from global_services.data.provider import DataProvider


class ReportGenerator:
    def __init__(self, strategy_name):
        self.strategy_name = strategy_name

        self.started_at = time.time()
        self.report_directory = None
        self.replay_start_time = None
        self.session_pair_start_time = None

        EventBus().subscribe(EventBusMsgType.SESSION_PAIR_START, self._reset_session_pair_start_time)
        EventBus().subscribe(EventBusMsgType.SESSION_PAIR_END, self.generate_session_pair_report)
        EventBus().subscribe(EventBusMsgType.PRICE_UPDATE, self._capture_replay_start_time)
        EventBus().subscribe(EventBusMsgType.SESSION_PAIR_END, self.generate_replay_summary)

    def _reset_session_pair_start_time(self):
        self.session_pair_start_time = None

    def _capture_replay_start_time(self):
        if self.replay_start_time is None:
            self.replay_start_time = DataProvider().get_time()

        if self.session_pair_start_time is None:
            self.session_pair_start_time = DataProvider().get_time()

    def generate_session_pair_report(self):
        symbol = DataProvider().get_symbol()
        session_number = self.session_counter.session
        report_directory = self._get_report_directory()
        report_path = report_directory / f"session_{session_number}-{symbol}.pdf"

        self._render_pdf(
            report_path,
            f"Session {session_number} - {symbol}",
            self._get_session_time_range(),
            self.session_pair_equity_visualizer,
            self.session_pair_statistics_visualizer,
        )

    def _get_session_time_range(self):
        if self.session_pair_start_time is None:
            return "Session time unavailable"

        start_time = datetime.fromtimestamp(self.session_pair_start_time / 1000)
        end_time = datetime.fromtimestamp(DataProvider().get_time() / 1000)
        return f"{start_time:%Y-%m-%d %H:%M:%S} - {end_time:%Y-%m-%d %H:%M:%S}"

    def generate_replay_summary(self):
        if self.replay_start_time is None:
            return

        report_path = self._get_report_directory() / "summary.pdf"
        self._render_pdf(
            report_path,
            "Summary",
            self._get_replay_time_range(),
            self.cumulative_equity_visualizer,
            self.cumulative_statistics_visualizer,
        )

    def _get_replay_time_range(self):
        start_time = datetime.fromtimestamp(self.replay_start_time / 1000)
        end_time = datetime.fromtimestamp(DataProvider().get_time() / 1000)
        return f"{start_time:%Y-%m-%d %H:%M:%S} - {end_time:%Y-%m-%d %H:%M:%S}"

    def _get_report_directory(self):
        if self.report_directory is None:
            started_at = datetime.fromtimestamp(self.started_at).strftime("%Y-%m-%d_%H-%M-%S")
            self.report_directory = Path("reports") / f"{started_at}-{self.strategy_name}"
            self.report_directory.mkdir(parents=True, exist_ok=True)
        return self.report_directory

    def _render_pdf(self, report_path, title, time_range, equity_visualizer, statistics_visualizer):
        page_width, page_height = A4
        pdf = canvas.Canvas(str(report_path), pagesize=A4)

        pdf.setFillColor(colors.HexColor("#121212"))
        pdf.rect(0, 0, page_width, page_height, fill=1, stroke=0)
        pdf.setFillColor(colors.white)
        pdf.setFont("Helvetica-Bold", 20)
        pdf.drawString(40, page_height - 50, title)
        pdf.setFont("Helvetica", 10)
        pdf.setFillColor(colors.HexColor("#aaaaaa"))
        pdf.drawString(40, page_height - 68, time_range)

        content_width = page_width - 80
        self._draw_equity_curve(pdf, 40, 400, content_width, 300, equity_visualizer)
        self._draw_statistics(pdf, 40, 370, content_width, statistics_visualizer)
        pdf.save()

    def _draw_statistics(self, pdf, x, top, width, statistics_visualizer):
        categories, values = statistics_visualizer.get_panel_content()
        pdf.setFont("Helvetica-Bold", 13)
        pdf.drawString(x, top, "Statistics")

        panel_top = top - 8
        panel_bottom = top - 28 - max(len(categories) - 1, 0) * 24 - 12
        pdf.setStrokeColor(colors.HexColor("#555555"))
        pdf.rect(x, panel_bottom, width, panel_top - panel_bottom, fill=0, stroke=1)

        pdf.setFont("Helvetica", 10)
        for index, (category, value) in enumerate(zip(categories, values)):
            y = top - 28 - index * 24
            pdf.setFillColor(colors.HexColor("#aaaaaa"))
            pdf.drawString(x, y, category)
            pdf.setFillColor(self._value_color(value))
            pdf.drawRightString(x + width - 12, y, self._value_text(value))

    def _draw_equity_curve(self, pdf, x, y, width, height, equity_visualizer):
        left_margin = 54
        bottom_margin = 28
        plot_x = x + left_margin
        plot_y = y + bottom_margin
        plot_width = width - left_margin
        plot_height = height - bottom_margin

        pdf.setFillColor(colors.white)
        pdf.setFont("Helvetica-Bold", 13)
        pdf.drawString(x, y + height + 18, "Equity Curve")
        pdf.setStrokeColor(colors.HexColor("#555555"))
        pdf.rect(plot_x, plot_y, plot_width, plot_height, fill=0, stroke=1)

        trace = equity_visualizer.get_traces()
        shapes = equity_visualizer.get_shapes()
        timestamps = list(trace.x)
        values = [float(value) for value in trace.y]
        if not values:
            pdf.setFont("Helvetica", 10)
            pdf.setFillColor(colors.HexColor("#aaaaaa"))
            pdf.drawCentredString(plot_x + plot_width / 2, plot_y + plot_height / 2, "No equity data")
            return

        minimum, maximum = min(values), max(values)
        shape_values = [
            float(shape["y0"])
            for shape in shapes
            if shape.get("type") == "line" and shape.get("yref") == "y"
        ]
        if shape_values:
            minimum = min(minimum, *shape_values)
            maximum = max(maximum, *shape_values)
        value_range = maximum - minimum or 1
        start_time = timestamps[0]
        end_time = timestamps[-1]
        time_range = (end_time - start_time).total_seconds() or 1

        pdf.setFont("Helvetica", 8)
        pdf.setStrokeColor(colors.HexColor("#333333"))
        pdf.setFillColor(colors.HexColor("#aaaaaa"))
        for tick_index in range(5):
            ratio = tick_index / 4
            tick_value = minimum + value_range * ratio
            tick_y = plot_y + plot_height * ratio
            pdf.line(plot_x, tick_y, plot_x + plot_width, tick_y)
            pdf.drawRightString(plot_x - 6, tick_y - 3, f"{tick_value:,.2f}")

        for tick_index in range(4):
            ratio = tick_index / 3
            tick_time = start_time + (end_time - start_time) * ratio
            tick_x = plot_x + plot_width * ratio
            pdf.line(tick_x, plot_y, tick_x, plot_y + plot_height)
            pdf.drawCentredString(tick_x, plot_y - 16, tick_time.strftime("%H:%M:%S"))

        pdf.setFillColor(colors.HexColor("#aaaaaa"))
        pdf.drawCentredString(plot_x + plot_width / 2, y + 4, "Time")
        pdf.saveState()
        pdf.translate(x + 12, plot_y + plot_height / 2)
        pdf.rotate(90)
        pdf.drawCentredString(0, 0, "Balance")
        pdf.restoreState()

        points = [
            (
                plot_x + (timestamp - start_time).total_seconds() / time_range * plot_width,
                plot_y + (value - minimum) / value_range * plot_height
            )
            for timestamp, value in zip(timestamps, values)
        ]

        path = pdf.beginPath()
        path.moveTo(*points[0])
        for point in points[1:]:
            path.lineTo(*point)
        pdf.setStrokeColor(colors.toColor(trace.line.color))
        pdf.setLineWidth(trace.line.width)
        pdf.drawPath(path, stroke=1, fill=0)

        for shape in shapes:
            if shape.get("type") != "line" or shape.get("yref") != "y":
                continue

            line = shape.get("line", {})
            line_color = line.get("color", "#ffffff")
            if line_color.startswith("rgba"):
                line_color = colors.HexColor(
                    "#ffffff" if "255,255,255" in line_color else "#ff4100"
                )
            else:
                line_color = colors.HexColor(line_color)

            line_y = plot_y + (float(shape["y0"]) - minimum) / value_range * plot_height
            pdf.setStrokeColor(line_color)
            pdf.setLineWidth(line.get("width", 1))
            pdf.setDash(1, 2) if line.get("dash") == "dot" else pdf.setDash()
            pdf.line(plot_x, line_y, plot_x + plot_width, line_y)
            pdf.setDash()

    @staticmethod
    def _value_text(value):
        return str(getattr(value, "children", value))

    @staticmethod
    def _value_color(value):
        style = getattr(value, "style", {})
        return colors.HexColor(style.get("color", "#ffffff"))

    def set_session_counter(self, session_counter: SessionCounter):
        self.session_counter = session_counter
        return self

    def set_equity_curve_visualizers(self, session_pair_visualizer: EquityCurveVisualizer, cumulative_visualizer: EquityCurveVisualizer):
        self.session_pair_equity_visualizer = session_pair_visualizer
        self.cumulative_equity_visualizer = cumulative_visualizer
        return self
    
    def set_statistics_visualizers(self, session_pair_visualizer: StatisticsVisualizer, cumulative_visualizer: StatisticsVisualizer):
        self.session_pair_statistics_visualizer = session_pair_visualizer
        self.cumulative_statistics_visualizer = cumulative_visualizer
        return self