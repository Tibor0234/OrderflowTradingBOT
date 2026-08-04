from decimal import Decimal
from dataclasses import dataclass

@dataclass(slots=True)
class OrderBookRow:
    price: Decimal
    quantity: Decimal

@dataclass(slots=True)
class OrderBookMessage:
    time: int
    bids: list[OrderBookRow]
    asks: list[OrderBookRow]