from data_analysis.statistics.base import BaseStatistics

class CumulativeStatistics(BaseStatistics):
    def __init__(self):
        self.starting_balance = None
        super().__init__()
    
    def session_start(self, starting_balance):
        if self.starting_balance is None:
            self.starting_balance = starting_balance
            self.equity = starting_balance
            self._max_equity = starting_balance
            self._update_count = 0