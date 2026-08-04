from decimal import Decimal
from data_managers.base import DataManager
from data_managers.order_book.subscriber import OrderBookManagerSubscriber
from data_managers.order_book.utils import OrderBookMessage, OrderBookRow

class OrderBookManager(DataManager):
    def __init__(self):
        self.subscribers: list[OrderBookManagerSubscriber] = []

    def subscribe(self, subscriber: OrderBookManagerSubscriber):
        self.subscribers.append(subscriber)
        return self

    def forward_message(self, msg):
        conv_msg = OrderBookMessage(
            time=int(msg["E"]),
            bids=[OrderBookRow(Decimal(price), Decimal(qty)) for price, qty in (msg.get("b") or msg.get("bids") or [])],
            asks=[OrderBookRow(Decimal(price), Decimal(qty)) for price, qty in (msg.get("a") or msg.get("asks") or [])],
        )

        for sub in self.subscribers:
            sub.process_message(conv_msg)