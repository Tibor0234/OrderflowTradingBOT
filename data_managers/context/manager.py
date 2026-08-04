from decimal import Decimal
from data_managers.context.utils import ContextPeriod
from data_managers.base import DataManager
from data_managers.context.subscriber import ContextManagerSubscriber
from data_managers.context.utils import ContextMessage, ContextCandle

class ContextManager(DataManager):
    def __init__(self):
        self.subscribers: list[ContextManagerSubscriber] = []

    def subscribe(self, subscriber: ContextManagerSubscriber):
        self.subscribers.append(subscriber)
        return self

    def forward_message(self, msg):
        conv_msg = ContextMessage(
            period=ContextPeriod(msg["period"]),
            timeframe=msg["interval"],
            candles=[
                ContextCandle(
                    time=int(c["open_time"]),
                    open=Decimal(c["open"]),
                    high=Decimal(c["high"]),
                    low=Decimal(c["low"]),
                    close=Decimal(c["close"]),
                    volume=Decimal(c["volume"]),
                )
                for c in msg["candles"]
            ]
        )

        for sub in self.subscribers:
            if sub.period == conv_msg.period:
                sub.process_message(conv_msg)