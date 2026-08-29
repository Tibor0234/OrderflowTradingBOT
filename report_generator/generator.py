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

        EventBus().subscribe(EventBusMsgType.SESSION_PAIR_END, self.generate_session_pair_report)
        EventBus().subscribe(EventBusMsgType.SESSION_PAIR_END, self.generate_backtest_summary)

    def generate_session_pair_report(self):
        symbol = DataProvider().get_symbol()
        session_number = self.session_counter.session
        report_directory = self._get_report_directory()
        report_path = report_directory / f"session_pair_{session_number}-{symbol}.pdf"

        self._render_pdf(report_path, session_number, symbol)

    def generate_backtest_summary(self):
        pass

    def _get_report_directory(self):
        if self.report_directory is None:
            started_at = datetime.fromtimestamp(self.started_at).strftime("%Y-%m-%d_%H-%M-%S")
            self.report_directory = Path("reports") / f"{started_at}-{self.strategy_name}"
            self.report_directory.mkdir(parents=True, exist_ok=True)
        return self.report_directory

    def _render_pdf(self, report_path, session_pair_number, symbol):
        page_width, page_height = A4
        pdf = canvas.Canvas(str(report_path), pagesize=A4)

        pdf.setFillColor(colors.HexColor("#121212"))
        pdf.rect(0, 0, page_width, page_height, fill=1, stroke=0)
        pdf.setFillColor(colors.white)
        pdf.setFont("Helvetica-Bold", 20)
        pdf.drawString(40, page_height - 50, f"Session pair {session_pair_number} - {symbol}")

        self._draw_equity_curve(pdf, 40, 400, page_width - 80, 300)
        self._draw_statistics(pdf, 40, 370)
        pdf.save()

    def _draw_statistics(self, pdf, x, top):
        categories, values = self.session_pair_statistics_visualizer.get_panel_content()
        pdf.setFont("Helvetica-Bold", 13)
        pdf.drawString(x, top, "Session Pair Statistics")

        pdf.setFont("Helvetica", 10)
        for index, (category, value) in enumerate(zip(categories, values)):
            y = top - 28 - index * 24
            pdf.setFillColor(colors.HexColor("#aaaaaa"))
            pdf.drawString(x, y, category)
            pdf.setFillColor(self._value_color(value))
            pdf.drawRightString(270, y, self._value_text(value))

    def _draw_equity_curve(self, pdf, x, y, width, height):
        pdf.setFillColor(colors.white)
        pdf.setFont("Helvetica-Bold", 13)
        pdf.drawString(x, y + height + 18, "Equity Curve")
        pdf.setStrokeColor(colors.HexColor("#555555"))
        pdf.rect(x, y, width, height, fill=0, stroke=1)

        trace = self.session_pair_equity_visualizer.get_traces()
        shapes = self.session_pair_equity_visualizer.get_shapes()
        values = [float(value) for value in trace.y]
        if not values:
            pdf.setFont("Helvetica", 10)
            pdf.setFillColor(colors.HexColor("#aaaaaa"))
            pdf.drawCentredString(x + width / 2, y + height / 2, "No equity data")
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
        step = width / max(len(values) - 1, 1)
        points = [
            (x + index * step, y + (value - minimum) / value_range * height)
            for index, value in enumerate(values)
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

            line_y = y + (float(shape["y0"]) - minimum) / value_range * height
            pdf.setStrokeColor(line_color)
            pdf.setLineWidth(line.get("width", 1))
            pdf.setDash(1, 2) if line.get("dash") == "dot" else pdf.setDash()
            pdf.line(x, line_y, x + width, line_y)
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

    def set_equity_curve_visualizer(self, session_pair_visualizer: EquityCurveVisualizer):
        return self.set_equity_curve_visualizers(session_pair_visualizer, None)
    
    def set_statistics_visualizers(self, session_pair_visualizer: StatisticsVisualizer, cumulative_visualizer: StatisticsVisualizer):
        self.session_pair_statistics_visualizer = session_pair_visualizer
        self.cumulative_statistics_visualizer = cumulative_visualizer
        return self

    def set_statistics_visualizer(self, session_pair_visualizer: StatisticsVisualizer):
        return self.set_statistics_visualizers(session_pair_visualizer, None)