from data_analysis.equity_curve.base import BaseEquityCurve
from global_services.data.provider import DataProvider

class CumulativeEquityCurve(BaseEquityCurve):
    def __init__(self, refresh_rate=1000):
        self.content = {}
        self.starting_equity = None
        self.session_boundaries = []
        
        self.refresh_rate = refresh_rate
        self.update_count = 0

        self.last_chart_time = 0
        self.session_point_count = 0
        self.session_start = None

    def is_initialized(self):
        return self.session_point_count >= 2
    
    def start_session(self):
        self.session_point_count = 0
        self.update_count = 0
        self.session_start = None

    def update(self, equity):
        self.update_count += 1

        if self.starting_equity is None:
            self.starting_equity = equity

        if not self.is_initialized() or self.update_count >= self.refresh_rate:
            time = DataProvider().get_time()

            if self.session_start is None:
                self.session_start = time
                chart_time = self.last_chart_time + (time - self.session_start)
                self.session_boundaries.append(chart_time)
            else:
                chart_time = self.last_chart_time + (time - self.session_start)

            self.content[chart_time] = equity
            self.last_chart_time = chart_time

            self.session_point_count += 1
            self.update_count = 0