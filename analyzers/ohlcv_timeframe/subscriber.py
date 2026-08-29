from abc import ABC, abstractmethod

class OHLCVTimeframeSubscriber(ABC):
    @abstractmethod
    def set_period(self, period):
        pass

    @abstractmethod
    def on_ohlcv_timeframe_update(self):
        pass