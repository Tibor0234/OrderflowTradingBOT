from dataclasses import dataclass
from decimal import Decimal

@dataclass(slots=True)
class OpenInterestMessage:
    time: int
    open_interest: Decimal