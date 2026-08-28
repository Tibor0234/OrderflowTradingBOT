from dataclasses import dataclass
from decimal import Decimal

from trading.market_entities.utils import Side


@dataclass(slots=True)
class BigTradeRecord:
	time: int
	price: Decimal
	quantity: Decimal
	side: Side