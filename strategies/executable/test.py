from decimal import Decimal
from strategies.core.base_strategy import BaseStrategy

class TestStrategy(BaseStrategy):
    def on_candle_close(self, candle_sec):
        if self.fw.is_trade_open() or self.fw.is_order_pending():
            return
        
        cvd_1m = self.fw.get_volume_delta("cvd_1m")

        if cvd_1m.current is not None:
            print(cvd_1m.current.value)

            if cvd_1m.current.value > Decimal(0):
                order = self.fw.place_market_order(
                    side=1,
                    value=1000,
                    leverage=10
                )
                print("order placed")