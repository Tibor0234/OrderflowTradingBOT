from enum import Enum
from decimal import Decimal
from dataclasses import dataclass

class OHLCVPeriod(Enum):
    LAST_DAY = 'last_day'
    LAST_WEEK = 'last_week'

@dataclass(slots=True)
class OHLCVCandle:
    time: int
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal

@dataclass(slots=True)
class OHLCVMessage:
    period: OHLCVPeriod
    timeframe: str
    candles: list[OHLCVCandle]