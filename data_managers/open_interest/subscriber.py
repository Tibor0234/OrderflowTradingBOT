from abc import ABC, abstractmethod

class OpenInterestManagerSubscriber(ABC):
    @abstractmethod
    def process_message(self, msg):
        pass