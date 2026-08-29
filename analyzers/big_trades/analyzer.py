from collections import deque
from decimal import Decimal
from math import ceil

from session_pairs.resource import Resource
from data_managers.trade.subscriber import TradeManagerSubscriber
from data_managers.trade.utils import TradeMessage
from analyzers.big_trades.model import BigTrades
from analyzers.big_trades.utils import BigTradeRecord


class BigTradesAnalyzer(Resource, TradeManagerSubscriber):
	def __init__(self, length=50, sample_size=500, top_pct=5, visualize=True):
		if length < 1:
			raise ValueError("length must be at least 1")
		if sample_size < 1:
			raise ValueError("sample_size must be at least 1")
		if not 0 < top_pct <= 100:
			raise ValueError("top_pct must be between 0 and 100")

		self.model: BigTrades = BigTrades(length)
		self.sample_size = sample_size
		self.top_rate = Decimal(str(top_pct)) / Decimal(100)
		self._quantities: deque[Decimal] = deque(maxlen=sample_size)

		self.visualize = visualize

	@property
	def visualizer(self):
		if self.visualize:
			from visualizers.price_chart.big_trades import BigTradesVisualizer
			return BigTradesVisualizer(self.model)
		return None

	def reset(self):
		self.model.content.clear()
		self._quantities.clear()

	def process_message(self, msg: TradeMessage):
		if self.is_big_trade(msg.quantity):
			self.model.content.append(BigTradeRecord(
				time=msg.time,
				price=msg.price,
				quantity=msg.quantity,
				side=msg.side,
			))

		self._quantities.append(msg.quantity)

	def is_big_trade(self, quantity: Decimal) -> bool:
		"""Returns whether quantity is in the rolling top volume range."""
		if not self._quantities:
			return False

		sorted_quantities = sorted(self._quantities)
		rank = ceil((1 - self.top_rate) * len(sorted_quantities))
		threshold = sorted_quantities[max(0, rank - 1)]

		return quantity >= threshold
