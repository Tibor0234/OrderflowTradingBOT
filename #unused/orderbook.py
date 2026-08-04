from sortedcontainers import SortedDict
from sessions.session_based_object import SessionBasedObject
from abc import ABC, abstractmethod
from collections.abc import Iterable
from market_data_managers.order_book_manager import OrderBookManagerSubscriber

class OrderBookSubsciber(ABC):
    @abstractmethod
    def on_orderbook_update(self):
        pass

class OrderBook(SessionBasedObject, OrderBookManagerSubscriber):
    def __init__(self, symbol):
        self.symbol = symbol
        self.time = None

        self.book = {
                'bids': SortedDict(lambda x: -x),
                'asks': SortedDict()
        }

        self.subscribers: list[OrderBookSubsciber] = []

    def reset(self):
        self.time = None
        self.book = self.book = {
                'bids': SortedDict(lambda x: -x),
                'asks': SortedDict()
        }

    def subscribe(self, subscriber: OrderBookSubsciber):
        self.subscribers.append(subscriber)
        return self

    def process_message(self, msg):
        self.time = msg['time']

        sides = [
            ('bids', msg.get('bids') or []),
            ('asks', msg.get('asks') or [])
        ]

        for side_name, orders in sides:
            book_side = self.book[side_name]
            for price, qty in orders:
                if qty == 0:
                    book_side.pop(price, None)
                else:
                    book_side[price] = qty

        for sub in self.subscribers:
            sub.on_orderbook_update()

    def get_best_bid(self):
        return next(iter(self.book['bids']), None)

    def get_best_ask(self):
        return next(iter(self.book['asks']), None)

    def get_min_bid(self):
        return next(reversed(self.book['bids']), None)

    def get_max_ask(self):
        return next(reversed(self.book['asks']), None)
