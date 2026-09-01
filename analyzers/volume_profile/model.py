from decimal import Decimal
from collections import deque
from analyzers.volume_profile.utils import PriceBin, POC, ValueArea, Volume

class VolumeProfile:
    """Stores rolling volume profile data and its derived metrics."""

    def __init__(self, price_bin_count: int, value_area_pct: int, length: int):
        """Initialize the volume profile configuration and state."""
        self.price_bin_count = price_bin_count
        self.length = length

        self.value_area_rate = Decimal(value_area_pct / 100)

        self.content: list[PriceBin] = []
        self.source: deque[Volume] = deque(maxlen=length)

        self.current: Volume | None = None
        self.poc: POC | None = None
        self.value_area: ValueArea | None = None