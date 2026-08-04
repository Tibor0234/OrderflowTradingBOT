from abc import ABC, abstractmethod
from decimal import Decimal

class BaseEquityCurve(ABC):
    def __init__(self):
        self.content: dict
        self.starting_equity: Decimal

    @abstractmethod
    def is_initialized(self):
        pass

    @abstractmethod
    def start_session(self):
        pass

    @abstractmethod
    def update(self, equity):
        pass