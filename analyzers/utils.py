from dataclasses import dataclass
from decimal import Decimal

@dataclass(slots=True)
class OscillatorRecord:
    """Stores an oscillator value at a specific point in time."""
    
    time: int
    value: Decimal