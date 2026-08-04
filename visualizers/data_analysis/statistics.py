from dash import html
from data_analysis.statistics.base import BaseStatistics
from visualizers.utils import colorize_number, format_number

class StatisticsVisualizer:
    def __init__(self, statistics: BaseStatistics):
        self.statistics = statistics

    def get_panel_content(self):
        categories = [
            "Total Trades",
            "Win Rate",
            "ROI",
            "Max Drawdown",
            "PnL (USD)",
            "Avg Win (USD)",
            "Avg Loss (USD)",
            "Expectancy (USD)",
            "Avg Trade Duration (m:s)"
        ]
        
        def format_trade_duration(seconds: float) -> str:
            minutes = int(seconds // 60)
            seconds = int(seconds % 60)
            return f"{minutes:02d}:{seconds:02d}"

        values = [
            self.statistics.total_trades,
            colorize_number(self.statistics.winrate, min_value=0.5, is_percentage=True),
            colorize_number(self.statistics.roi, min_value=0, is_percentage=True),
            f"{self.statistics.max_drawdown:.2%}",
            colorize_number(self.statistics.pnl, min_value=0),
            format_number(self.statistics.average_win),
            format_number(self.statistics.average_loss),
            colorize_number(self.statistics.expectency, min_value=0),
            format_trade_duration(self.statistics.average_trade_duration)
        ]

        return categories, values