from dataclasses import dataclass

@dataclass(slots=True)
class MonotonicTrend:
    """Stores the result of a monotonic trend analysis."""

    is_trending: bool
    trend_length: int
    trend_direction: int

@dataclass(slots=True)
class Outlier:
    """Stores the result and relative strength of an outlier analysis."""
    
    is_outlier: bool
    strength: float