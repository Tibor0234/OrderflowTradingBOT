import uuid
from abc import ABC
from trading.market_entities.utils import Side, OrderType
from decimal import Decimal
from global_services.data.provider import DataProvider
from trading.market_entities.stop_order import StopOrder
from trading.market_entities.increase_order import IncreaseOrder, IncreaseLimitOrder

class Order(ABC):
    def __init__(
        self,
        side: Side,
        value: Decimal,
        entry_price: Decimal,
        type: OrderType,
        leverage: float,
        kill: int = None,
        kill_after_fill: int = None
    ):
        self.id = uuid.uuid4()
        self.type: OrderType = type
        self.side: Side = side
        self.entry_price: Decimal = entry_price
        self.value: Decimal = value
        self.leverage: Decimal = Decimal(leverage)

        # Kill timings
        self.kill: int | None = kill
        self.kill_after_fill: int | None = kill_after_fill
        self.place_time: int | None = None
        self.fill_time: int | None = None


    def place(self):
        self.place_time = DataProvider().get_time()

    def on_partial_fill(self):
        self.fill_time = DataProvider().get_time()

    def is_filled(self) -> bool:
        return self.value <= 0

    def is_killed(self) -> bool:
        now = DataProvider().get_time()
        
        if not self.place_time:
            return False

        if not self.fill_time:
            if self.kill and (now - self.place_time) >= self.kill:
                return True
        else:
            if self.kill_after_fill and (now - self.fill_time) >= self.kill_after_fill:
                return True

        return False

    def link(self, linked_order: IncreaseOrder | StopOrder):
        linked_order.set_from_source(self.id, self.side)
        return self
    
    def link_many(self, linked_orders: list[IncreaseOrder | StopOrder]):
        if not isinstance(linked_orders, list):
            linked_orders = [linked_orders]
        
        for linked_order in linked_orders:
            self.link(linked_order)
            
        return self

    def is_triggered(self) -> bool:
        if self.type == OrderType.MARKET:
            return True
        price = DataProvider().get_price()
        return (price - self.entry_price) * (-self.side.value) >= 0
    
    def convert_to_increase_order(self) -> IncreaseLimitOrder:
        return IncreaseLimitOrder(self.value, self.entry_price, self.leverage, self.kill_after_fill)


class LimitOrder(Order):
    def __init__(self, side: Side, value: Decimal, entry_price: Decimal, leverage: float = 1.0, kill: int = None, kill_after_fill: int = None):
        super().__init__(side=side, value=value, entry_price=entry_price, type=OrderType.LIMIT, leverage=leverage, kill=kill, kill_after_fill=kill_after_fill)

class MarketOrder(Order):
    def __init__(self, side: Side, value: Decimal, leverage: float = 1.0):
        super().__init__(side=side, value=value, entry_price=None, type=OrderType.MARKET, leverage=leverage, kill=None, kill_after_fill=None)