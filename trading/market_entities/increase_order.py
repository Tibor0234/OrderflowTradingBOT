import uuid
from decimal import Decimal
from trading.market_entities.utils import Side, OrderType
from global_services.data.provider import DataProvider

class IncreaseOrder():
    def __init__(self, value: Decimal, entry_price: Decimal, type: OrderType, leverage: float = 1.0, kill_after_fill = None, metadata: dict[str, object] | None = None):
        self.source_id: uuid.UUID | None = None
        self.side: Side | None = None
        self.type = type
        self.value = Decimal(value)
        self.entry_price = Decimal(entry_price) if entry_price is not None else None
        self.leverage = Decimal(leverage)
        self.metadata = dict(metadata) if metadata else {}

        self.fill_time = None
        self.kill_after_fill = kill_after_fill

    def set_from_source(self, source_id: uuid.UUID, side: Side):
        self.source_id = source_id
        self.side = side

    def is_filled(self) -> bool:
        return self.value <= 0

    def is_triggered(self) -> bool:
        if self.type == OrderType.MARKET:
            return True
        current_price = DataProvider().get_price()
        return (current_price - self.entry_price) * (-self.side.value) >= 0
    
    def on_partial_fill(self):
        self.fill_time = DataProvider().get_time()

    def is_killed(self):
        now = DataProvider().get_time()
        if not self.kill_after_fill or not self.fill_time:
            return False
        return (now - self.fill_time) >= self.kill_after_fill

class IncreaseLimitOrder(IncreaseOrder):
    def __init__(self, value: Decimal, entry_price: Decimal, leverage: float = 1.0, kill_after_fill: int = None, metadata: dict[str, object] | None = None):
        super().__init__(value=value, entry_price=entry_price, type=OrderType.LIMIT, leverage=leverage, kill_after_fill=kill_after_fill, metadata=metadata)

class IncreaseMarketOrder(IncreaseOrder):
    def __init__(self, value: Decimal, leverage: float = 1.0, metadata: dict[str, object] | None = None):
        super().__init__(value=value, entry_price=None, type=OrderType.MARKET, leverage=leverage, kill_after_fill=None, metadata=metadata)