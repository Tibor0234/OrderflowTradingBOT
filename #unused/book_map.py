from collections import deque
from model.orderbook import OrderBook
from sessions.session_based_object import SessionBasedObject
from model.orderbook import OrderBookSubsciber
from utils import DEFAULT


class BookMap(SessionBasedObject, OrderBookSubsciber):
    def __init__(self, order_book: OrderBook, compress_by, max_depth, max_history=DEFAULT, refresh_rate=DEFAULT):
        """Default max history = 100
           Default refresh rate = 10"""
        self.order_book = order_book
        self.compress_by = compress_by
        self.max_depth = max_depth
        self.max_history = 100 if max_history is DEFAULT else max_history
        self.refresh_rate = 10 if refresh_rate is DEFAULT else refresh_rate

        self.is_default = (
            max_depth is DEFAULT
            and refresh_rate is DEFAULT
        )

        self.content = deque(maxlen=self.max_history)

        self.update_count = 0

    def reset(self):
        self.content.clear()
        self.update_count = 0

    def on_order_book_update(self):
        self.update_count += 1
        if self.update_count >= self.refresh_rate:
            self.get_snapshot()
            self.update_count = 0
        
    def get_snapshot(self):
        book = self.order_book.book
        compressed_bins = {'bids': [], 'asks': []}

        for side in ['bids', 'asks']:
            bins = []
            counter = 0
            bin = None

            # Top max_depth elemek lekérése
            if side == 'bids':
                prices = list(book[side].items())[:self.max_depth]
            else:
                prices = list(book[side].items())[:self.max_depth]

            for price, qty in prices:
                if bin is None:
                    # ha még nincs bin, létrehozunk egyet
                    bin = {'top': price, 'bottom': price, 'qty': qty}
                    counter = 1
                    continue

                if counter >= self.compress_by:
                    # előző bin mentése
                    bins.append(bin)
                    # új bin létrehozása az aktuális elemmel
                    bin = {'top': price, 'bottom': price, 'qty': qty}
                    counter = 1
                else:
                    # bin frissítése
                    bin['top'] = max(bin['top'], price)
                    bin['bottom'] = min(bin['bottom'], price)
                    bin['qty'] += qty
                    counter += 1

            if bin is not None:
                bins.append(bin)

            compressed_bins[side] = bins

        compressed_bins['time'] = self.order_book.time
        self.content.append(compressed_bins)