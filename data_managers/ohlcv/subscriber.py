from abc import ABC, abstractmethod
from data_managers.ohlcv.utils import OHLCVPeriod

class OHLCVManagerSubscriber(ABC):
    def __init__(self):
        self.period: OHLCVPeriod

    @abstractmethod
    def process_message(self, msg):
        pass