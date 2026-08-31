from abc import ABC
from trading.market_entities.trade import Trade
from strategies.core.framework import StrategyFramework
from global_services.events.bus import EventBus
from global_services.events.utils import EventBusMsgType
from data_managers.trade.utils import TradeMessage

class BaseStrategy(ABC):
    def init(self, framework: StrategyFramework):
        self.fw = framework

        EventBus().subscribe(EventBusMsgType.SESSION_PAIR_START, self.on_session_pair_start)
        EventBus().subscribe(EventBusMsgType.PRICE_UPDATE, self.on_price_update)
        EventBus().subscribe(EventBusMsgType.CANDLE_CLOSE, self.on_candle_close)
        EventBus().subscribe(EventBusMsgType.TRADE_CLOSE, self.on_trade_close)

    #on signal metódusok
    def on_session_pair_start(self):
        pass

    def on_price_update(self):
        pass

    def on_candle_close(self, candle_sec: int):
        pass

    def on_big_trade(self, msg: TradeMessage, top_pct: float):
        pass

    def on_trade_close(self, trade: Trade):
        pass