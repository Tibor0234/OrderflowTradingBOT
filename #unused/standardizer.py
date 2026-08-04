from collections import deque
from sessions.session_based_object import SessionBasedObject
from decimal import Decimal

class Standardizer(SessionBasedObject):
    def __init__(self, smoothing_pct=50):
        self.alpha = self._calculate_alpha(smoothing_pct)
        self.mean = None
        self.variance = None

    def _calculate_alpha(self, smoothing_pct):
        smoothing_pct = max(0, min(100, smoothing_pct))
        alpha_min = Decimal("0.01")
        alpha_max = Decimal("0.3")
        t = (Decimal("100") - Decimal(smoothing_pct)) / Decimal("100")
        return alpha_min * (alpha_max / alpha_min) ** t

    def reset(self):
        self.mean = None
        self.variance = None

    def override(self, smoothing_pct):
        if smoothing_pct is not None:
            self.alpha = self._calculate_alpha(smoothing_pct)

    def get_value(self, value):
        raise NotImplementedError("get_value method must be implemented by subclass")

class ZScoreStandardizer(Standardizer):
    def __init__(self, smoothing_pct=50):
        super().__init__(smoothing_pct)

    def get_value(self, value):
        if self.mean is None or self.variance is None:
            self.mean = value
            self.variance = Decimal(0)
            return Decimal(0)

        alpha = self.alpha
        delta = value - self.mean
        self.mean += alpha * delta
        self.variance += alpha * (delta ** 2 - self.variance)

        std = self.variance.sqrt() if self.variance > 0 else Decimal(0)
        if std == 0:
            return Decimal(0)

        return (value - self.mean) / std

class _CumulativeStandardizer(Standardizer):
    def __init__(self, smoothing_pct=50):
        super().__init__(smoothing_pct)
        self.previous_value = None

    def reset(self):
        super().reset()
        self.previous_value = None

    def get_value(self, value):
        if self.previous_value is None:
            self.previous_value = value
            self.mean = Decimal(0)
            self.variance = Decimal(0)
            return Decimal(0)

        delta = value - self.previous_value
        self.previous_value = value

        if self.mean is None:
            self.mean = delta
        else:
            self.mean += self.alpha * (delta - self.mean)

        if self.variance is None:
            self.variance = Decimal(0)
        else:
            self.variance += self.alpha * ((delta - self.mean) ** 2 - self.variance)

        std = self.variance.sqrt() if self.variance > 0 else Decimal(0)

        if std == 0:
            return Decimal(0)

        return (delta - self.mean) / std

class CumulativeStandardizer(SessionBasedObject):
    """
    Trendet követő normalizálás kumulált adatokhoz.
    - Követi a trendet, nem cikcakkos
    - Kimenet 0..1
    - Opcionális EMA smoothing
    """
    def __init__(self, smoothing_pct: int = 50):
        """
        :param smoothing_pct: 0..100, 100 = nagyon sima EMA smoothing
        """
        self.alpha = self._calculate_alpha(smoothing_pct)
        self.start_value: Decimal = None
        self.max_so_far: Decimal = None
        self.smoothed_value: Decimal = None

    def _calculate_alpha(self, smoothing_pct: int) -> Decimal:
        smoothing_pct = max(0, min(100, smoothing_pct))
        alpha_min = Decimal("0.01")
        alpha_max = Decimal("0.3")
        t = (Decimal("100") - Decimal(smoothing_pct)) / Decimal("100")
        return alpha_min * (alpha_max / alpha_min) ** t

    def reset(self):
        self.start_value = None
        self.max_so_far = None
        self.smoothed_value = None

    def override(self, smoothing_pct=None):
        if smoothing_pct is not None:
            self.alpha = self._calculate_alpha(smoothing_pct)

    def get_value(self, value):
        value = Decimal(value)

        # első érték inicializálása
        if self.start_value is None:
            self.start_value = value
            self.max_so_far = value
            self.smoothed_value = Decimal("0")
            return self.smoothed_value

        # max eddigi érték frissítése
        if value > self.max_so_far:
            self.max_so_far = value

        # normálás 0..1 közé
        denom = self.max_so_far - self.start_value
        if denom == 0:
            norm = Decimal("0")
        else:
            norm = (value - self.start_value) / denom

        # EMA smoothing
        if self.smoothed_value is None:
            self.smoothed_value = norm
        else:
            self.smoothed_value += self.alpha * (norm - self.smoothed_value)

        return self.smoothed_value