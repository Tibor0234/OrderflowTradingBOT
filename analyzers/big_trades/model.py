from collections import deque
from analyzers.big_trades.utils import BigTradeRecord

class BigTrades:
	def __init__(self, length: int = 50):
		self.length = length
		self.content: deque[BigTradeRecord] = deque(maxlen=length)

	@property
	def current(self) -> BigTradeRecord | None:
		return self.content[-1] if self.content else None
