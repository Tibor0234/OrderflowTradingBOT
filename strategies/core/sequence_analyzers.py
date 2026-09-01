import numpy as np
from global_services.data.provider import DataProvider
from strategies.core.utils import MonotonicTrend, Outlier

class SequenceAnalyzers:
    """Provides reusable methods for analyzing sequences of market data."""

    def has_min_length(self, sequence, length):
        """Return whether the sequence contains at least the specified number of elements."""
        return len(sequence) >= length

    def get_monotonic_trend(self, sequence, source_name):
        """Determine the direction and length of the latest monotonic trend."""
        if not sequence:
            return MonotonicTrend(False, 0, 0)

        if not hasattr(sequence[-1], source_name):
            raise AttributeError(f"{source_name} not found")

        if len(sequence) < 2:
            return MonotonicTrend(False, 0, 0)

        def v(i):
            return getattr(sequence[i], source_name)

        last, prev = v(-1), v(-2)

        if last == prev:
            return MonotonicTrend(False, 0, 0)

        direction = 1 if last > prev else -1
        length = 2

        for i in range(len(sequence) - 3, -1, -1):
            a, b = v(i), v(i + 1)

            if (direction == 1 and b > a) or (direction == -1 and b < a):
                length += 1
            else:
                break

        return MonotonicTrend(length >= 3, length, direction)
    
    def get_trend_strength(self, sequence, source_name, recent_bias_pct=0, length=None):
        """Calculate normalized trend strength with optional weighting toward recent values."""
        recent_bias_rate = recent_bias_pct / 100.0

        if length is None:
            length = len(sequence)

        if not sequence:
            return 0.0

        length = min(length, len(sequence))

        if length < 2:
            return 0.0

        seq = sequence[-length:]

        try:
            closes = np.array([float(getattr(c, source_name)) for c in seq])
        except AttributeError:
            raise AttributeError(f"{source_name} not found")

        if closes.size < 2:
            return 0.0

        if hasattr(seq[0], "time"):
            timestamps = np.array([c.time for c in seq])
            x = (timestamps.astype(float) - timestamps[0]) / 60
        else:
            x = np.arange(len(closes))

        n = len(closes)

        decay = (1 - recent_bias_rate)
        weights = decay ** (n - np.arange(n) - 1)

        try:
            slope, intercept = np.polyfit(x, closes, 1, w=weights)
        except Exception:
            return 0.0

        trend_move = slope * (x[-1] - x[0])

        volatility = np.std(np.diff(closes))
        scale_factor = np.log1p(len(closes)) * 2

        if volatility == 0:
            return 0.0

        raw = (trend_move / volatility) / scale_factor

        return float(np.tanh(raw))
    
    def get_outlier(self, sequence, source_name, length=None):
        """Detect whether the latest movement is an outlier relative to recent movements."""
        if length is None:
            length = len(sequence)

        if not sequence:
            return Outlier(False, 0.0)

        if not hasattr(sequence[-1], source_name):
            raise AttributeError(f"{source_name} not found")

        length = min(length, len(sequence) - 1)

        if length <= 0:
            return Outlier(False, 0.0)

        v = lambda i: getattr(sequence[i], source_name)

        diffs = [
            abs(v(i + 1) - v(i))
            for i in range(-length - 1, -1)
        ]

        avg = sum(diffs) / len(diffs) if diffs else 0
        last_diff = abs(v(-1) - v(-2))

        if avg == 0:
            ratio = 0.0 if last_diff == 0 else float("inf")
        else:
            ratio = last_diff / avg

        return Outlier(
            last_diff > avg,
            ratio if v(-1) >= v(-2) else -ratio
        )

    def get_local_swings(self, sequence, source_name, direction, swing_length, length=None):
        """Find local swing highs or lows within the specified sequence range."""
        if not sequence or swing_length <= 0:
            return []

        if length is None:
            length = len(sequence)
        if length <= 0:
            return []

        sequence = sequence[-length:]

        n = len(sequence)

        swing_length = min(swing_length, (n - 1) // 2)

        if swing_length <= 0:
            return []

        out = []
        g = getattr
        cmp = (lambda a, b: a < b) if direction == -1 else (lambda a, b: a > b)

        i = swing_length

        while i < n - swing_length:
            v = g(sequence[i], source_name)
            ok = True

            for j in range(1, swing_length + 1):
                if i - j < 0:
                    break
                if cmp(g(sequence[i - j], source_name), v):
                    ok = False
                    break

            if ok:
                for j in range(1, swing_length + 1):
                    if i + j >= n:
                        break
                    if cmp(g(sequence[i + j], source_name), v):
                        ok = False
                        break

            if ok:
                out.append(sequence[i])
                i += swing_length
            else:
                i += 1

        return out

    def get_big_trade_dominance(self, sequence, window_seconds=None, length=None):
        """Return volume-weighted big-trade dominance in the range [-1, 1]."""
        if window_seconds is not None and window_seconds <= 0:
            raise ValueError("window_seconds must be greater than 0")

        records = list(sequence)
        if length is not None:
            records = records[-length:]
        if window_seconds is not None and records:
            current_time = DataProvider().get_time()
            window_start = current_time - window_seconds * 1000
            records = [record for record in records if record.time >= window_start]

        if not records:
            return 0.0

        buy_volume = sum(
            float(record.quantity)
            for record in records
            if record.side.value > 0
        )
        sell_volume = sum(
            float(record.quantity)
            for record in records
            if record.side.value < 0
        )
        total_volume = buy_volume + sell_volume

        if total_volume == 0:
            return 0.0

        return (buy_volume - sell_volume) / total_volume

    def get_big_trade_intensity(self, sequence, window_seconds=60, length=None):
        """Return the number of big trades per minute in the time window."""
        if window_seconds <= 0:
            raise ValueError("window_seconds must be greater than 0")

        records = list(sequence)
        if length is not None:
            records = records[-length:]
        if records:
            current_time = DataProvider().get_time()
            window_start = current_time - window_seconds * 1000
            records = [record for record in records if record.time >= window_start]

        return len(records) * 60 / window_seconds