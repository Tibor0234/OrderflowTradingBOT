from abc import ABC, abstractmethod
from data_managers.trade.utils import TradeMessage

class TimeframeSubscriber(ABC):
    def init_model(self, length):
        pass

    @abstractmethod
    def on_timeframe_update(self, msg: TradeMessage):
        pass

    @abstractmethod
    def on_candle_close(self):
        pass