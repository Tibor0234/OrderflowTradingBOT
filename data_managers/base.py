from abc import ABC, abstractmethod

class DataManager(ABC):
    @abstractmethod
    def forward_message(self, msg):
        pass