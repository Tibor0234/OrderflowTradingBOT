from decimal import Decimal
from analyzers.context_volume_profile.utils import POC, ValueArea, ContextPriceBin

class ContextVolumeProfile:
    def __init__(self, price_bin_count: int = 24, value_area_pct: int = 70):
        self.period = None

        self.price_bin_count = price_bin_count
        self.value_area_rate = Decimal(value_area_pct / 100)

        self.content: list[ContextPriceBin] = []
        self.poc: POC | None = None
        self.value_area: ValueArea | None = None

        self.start_time = None