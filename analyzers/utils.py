from dataclasses import dataclass
from decimal import Decimal

@dataclass(slots=True)
class OscillatorRecord:
    time: int
    value: Decimal