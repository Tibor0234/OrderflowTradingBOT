from dataclasses import dataclass
from decimal import Decimal
from analyzers.volume_profile.utils import POC, ValueArea

@dataclass(slots=True)
class ContextPriceBin:
    low: Decimal
    size: Decimal
    volume: Decimal