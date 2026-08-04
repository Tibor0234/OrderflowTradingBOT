import uuid
from decimal import Decimal
from trading.market_entities.utils import Side, OrderType
from global_services.data.provider import DataProvider

class StopOrder:
    def __init__(self, price: Decimal, type: OrderType, close_rate: float = 1.0):
        self.source_id: uuid.UUID | None = None
        self.side: Side | None = None
        self.type = type
        self.price = Decimal(price) if price is not None else None
        self.close_rate = Decimal(close_rate)

    def set_from_source(self, source_id: uuid.UUID, side: Side):
        self.source_id = source_id
        self.side = side.opposite()

    def is_filled(self) -> bool:
        return self.close_rate <= 0

    def is_triggered(self, direction: int) -> bool:
        if self.price is None:
            return True
        current_price = DataProvider().get_price()
        return (current_price - self.price) * direction >= 0
    
    
class TakeProfit(StopOrder):
    def __init__(self, price: Decimal, type: OrderType, pct: float):
        super().__init__(price=price, type=type, close_rate=pct/100)

    def is_triggered(self):
        return super().is_triggered(-self.side.value)

class StopLoss(StopOrder):
    def __init__(self, price: Decimal):
        super().__init__(price=price, type=OrderType.MARKET, close_rate=1.0)

    def is_triggered(self):
        return super().is_triggered(self.side.value)

class LiquidationOrder(StopLoss):
    def __init__(self, price):
        super().__init__(price)

class ReduceOnly(StopOrder):
    def __init__(self, pct: float):
        super().__init__(price=None, type=OrderType.MARKET, close_rate=pct/100)