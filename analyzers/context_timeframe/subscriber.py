from abc import ABC, abstractmethod

class ContextTimeframeSubscriber(ABC):
    @abstractmethod
    def set_period(self, period):
        pass

    @abstractmethod
    def on_context_timeframe_update(self):
        pass