from strategies.core.essentials_package import *

class TestStrategy(BaseStrategy):
    def on_candle_close(self, candle_sec):
        if self.fw.is_trade_open() or self.fw.is_order_pending():
            return
        
        cvd_1m = self.fw.get_resource("vd_1m", VolumeDelta)

        if cvd_1m.current is not None:

            if cvd_1m.current.value > Decimal(0):
                order = self.fw.place_market_order(
                    side=1,
                    value=1000,
                    leverage=10
                )
