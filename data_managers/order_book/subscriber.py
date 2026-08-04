from abc import ABC, abstractmethod

class OrderBookManagerSubscriber(ABC):
    @abstractmethod
    def process_message(self, msg):
        pass