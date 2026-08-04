from decimal import Decimal
from data_managers.base import DataManager
from data_managers.open_interest.subscriber import OpenInterestManagerSubscriber
from data_managers.open_interest.utils import OpenInterestMessage

class OpenInterestManager(DataManager):
    def __init__(self):
        self.subscribers: list[OpenInterestManagerSubscriber] = []

    def subscribe(self, subscriber: OpenInterestManagerSubscriber):
        self.subscribers.append(subscriber)
        return self

    def forward_message(self, msg):
        conv_msg = OpenInterestMessage(
            time=int(msg["time"]),
            open_interest=Decimal(msg["openInterest"])
        )

        for sub in self.subscribers:
            sub.process_message(conv_msg)