from enum import Enum
from decimal import Decimal
from dataclasses import dataclass

class ContextPeriod(Enum):
    LAST_DAY = 'last_day'
    LAST_WEEK = 'last_week'

@dataclass(slots=True)
class ContextCandle:
    time: int
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal

@dataclass(slots=True)
class ContextMessage:
    period: ContextPeriod
    timeframe: str
    candles: list[ContextCandle]