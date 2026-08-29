from data_analysis.statistics.base import BaseStatistics

class SessionPairBasedStatistics(BaseStatistics):
    def __init__(self):
        super().__init__()

    def session_pair_start(self, starting_balance):
        self.starting_balance = starting_balance
        self.equity = starting_balance
        self._max_equity = starting_balance
        self._update_count = 0
        self._reset()
