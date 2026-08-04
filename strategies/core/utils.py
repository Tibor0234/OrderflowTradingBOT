from dataclasses import dataclass

@dataclass(slots=True)
class MonotonicTrend:
    is_trending: bool
    trend_length: int
    trend_direction: int

@dataclass(slots=True)
class Outlier:
    is_outlier: bool
    strength: float