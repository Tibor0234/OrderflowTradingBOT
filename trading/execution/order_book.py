from decimal import Decimal
from data_managers.order_book.manager import OrderBookManagerSubscriber, OrderBookMessage, OrderBookRow
from trading.market_entities.utils import Side

class ExecutionOrderBook(OrderBookManagerSubscriber):
    def __init__(self):
        self.bids: list[OrderBookRow] = []
        self.asks: list[OrderBookRow] = []

    def process_message(self, msg: OrderBookMessage):
        self.bids[:] = msg.bids
        self.asks[:] = msg.asks

    @property
    def best_bid(self) -> Decimal | None:
        if not self.bids:
            return None
        return self.bids[0].price

    @property
    def best_ask(self) -> Decimal | None:
        if not self.asks:
            return None
        return self.asks[0].price

    @property
    def spread(self) -> Decimal | None:
        if not self.bids or not self.asks:
            return None
        return self.best_ask - self.best_bid
    
    def _fill_order(self, value: Decimal, side: Side, book: list[OrderBookRow], limit_price: Decimal = None) -> tuple[Decimal, Decimal]:
        
        remaining = value
        total_cost = Decimal(0)
        filled_value = Decimal(0)
        last_price = None

        for row in book:
            # Limit ellenőrzés
            if limit_price is not None:
                if (side == Side.BUY and row.price > limit_price) or (side == Side.SELL and row.price < limit_price):
                    break

            fill_qty = min(row.quantity, remaining)
            total_cost += fill_qty * row.price
            filled_value += fill_qty
            remaining -= fill_qty
            last_price = row.price

            if remaining <= 0:
                break

        # Ha maradt még, market ordernél kitöltjük az utolsó áron
        if remaining > 0 and limit_price is None and last_price is not None:
            total_cost += remaining * last_price
            filled_value += remaining
            remaining = 0

        if filled_value == 0:
            return Decimal(0), Decimal(0)

        execution_price = total_cost / filled_value
        return execution_price, filled_value

    # ---------------- Nyilvános metódusok ----------------

    def calculate_limit_fill(self, value: Decimal, side: Side, entry_price: Decimal) -> tuple[Decimal, Decimal]:
        book_side = self.asks if side == Side.BUY else self.bids
        execution_price, filled_value = self._fill_order(value, side, book_side, limit_price=entry_price)
        return execution_price, filled_value

    def calculate_market_fill(self, value: Decimal, side: Side) -> Decimal:
        book_side = self.asks if side == Side.BUY else self.bids
        execution_price, _ = self._fill_order(value, side, book_side, limit_price=None)
        return execution_price