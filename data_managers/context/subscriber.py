from abc import ABC, abstractmethod
from data_managers.context.utils import ContextPeriod

class ContextManagerSubscriber(ABC):
    def __init__(self):
        self.period: ContextPeriod

    @abstractmethod
    def process_message(self, msg):
        pass