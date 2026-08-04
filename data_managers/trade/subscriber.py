from abc import ABC, abstractmethod

class TradeManagerSubscriber(ABC):
    @abstractmethod
    def process_message(self, msg):
        pass
