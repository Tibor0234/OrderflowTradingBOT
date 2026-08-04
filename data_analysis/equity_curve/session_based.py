from data_analysis.equity_curve.base import BaseEquityCurve
from global_services.data.provider import DataProvider

class SessionBasedEquityCurve(BaseEquityCurve):
    def __init__(self, refresh_rate=100):
        self.content = {}
        self.starting_equity = None
        
        self.refresh_rate = refresh_rate
        self.update_count = 0

    def is_initialized(self):
        return len(self.content) >= 2
    
    def start_session(self):
        self.content.clear()
        self.update_count = 0
        self.starting_equity = None

    def update(self, equity):
        self.update_count += 1

        if self.starting_equity is None:
            self.starting_equity = equity

        if not self.is_initialized() or self.update_count >= self.refresh_rate:
            time = DataProvider().get_time()

            self.content[time] = equity
            self.last_chart_time = time
            self.update_count = 0