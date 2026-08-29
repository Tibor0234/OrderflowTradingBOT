from abc import ABC, abstractmethod
from decimal import Decimal
from trading.market_entities.trade import Trade

class BaseStatistics(ABC):
    def __init__(self, refresh_rate=50):
        self._refresh_rate = refresh_rate
        self._update_count = 0

        self.starting_balance: Decimal
        
        self._reset()

    def _reset(self):
        self.total_trades = 0
        self.winrate = 0
        self.pnl = 0
        self.roi = 0
        self.max_drawdown = 0
        self.expectency = 0
        self.average_win = 0
        self.average_loss = 0
        self.average_trade_duration = 0

    @abstractmethod
    def session_pair_start(self, starting_balance):
        pass

    def update_on_trade_close(self, trade: Trade):
        self.total_trades += 1
        self.pnl += trade.realized_pnl

        if trade.realized_pnl > 0:
            self.winrate = ((self.winrate * (self.total_trades - 1)) + 1) / self.total_trades
            self.average_win = ((self.average_win * (self.total_trades - 1)) + trade.realized_pnl) / self.total_trades
        else:
            self.winrate = (self.winrate * (self.total_trades - 1)) / self.total_trades
            self.average_loss = ((self.average_loss * (self.total_trades - 1)) + trade.realized_pnl) / self.total_trades

        self.expectency = (self.winrate * float(self.average_win)) + ((1 - self.winrate) * float(self.average_loss))

        trade_duration_s = (trade.close_time - trade.open_time) / 1000
        if self.average_trade_duration != 0:
                self.average_trade_duration = (
                self.average_trade_duration * (self.total_trades - 1) + trade_duration_s
            ) / self.total_trades
        else:
            self.average_trade_duration = trade_duration_s

    def update_on_price_change(self, equity, force=False):
        self._update_count += 1

        if force or self._update_count >= self._refresh_rate:
            self.equity = equity
            self.roi = ((equity - self.starting_balance) / self.starting_balance)

            if equity > self._max_equity:
                self._max_equity = equity
            else:
                drawdown = ((self._max_equity - equity) / self._max_equity)
                if drawdown > self.max_drawdown:
                    self.max_drawdown = drawdown

            self._update_count = 0