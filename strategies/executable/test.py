from decimal import Decimal
from strategies.core.base_strategy import BaseStrategy

class TestStrategy(BaseStrategy):
    def on_candle_close(self, candle_sec):
        ctx_1d = self.fw.get_resource('ctx_1w')
        trend_strength = self.fw.get_trend_strength(ctx_1d.content, 'close', 3)
        return

        if self.fw.is_order_pending() or self.fw.is_trade_open():
            return
        
        entry_price = self.fw.get_current_price() * Decimal(1.001)
        
        self.fw.place_limit_order(side=-1, value=100, entry_price=entry_price, leverage=10)