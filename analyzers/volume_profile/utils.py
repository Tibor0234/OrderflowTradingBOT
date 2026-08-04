from dataclasses import dataclass
from decimal import Decimal

@dataclass(slots=True)
class PriceBin:
    low: Decimal
    size: Decimal
    buy_volume: Decimal
    sell_volume: Decimal

@dataclass(slots=True)
class Volume:
    high: Decimal | None
    low: Decimal | None
    buy_volume: Decimal
    sell_volume: Decimal

@dataclass(slots=True)
class POC:
    price: Decimal | None
    volume: Decimal

@dataclass(slots=True)
class ValueArea:
    high: Decimal | None
    low: Decimal | None