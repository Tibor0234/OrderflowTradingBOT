import numpy as np
from strategies.core.utils import MonotonicTrend, Outlier

class SequenceAnalyzers:
    def has_min_length(self, sequence, length):
        return len(sequence) >= length

    def get_monotonic_trend(self, sequence, source_name):
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