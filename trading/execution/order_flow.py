from decimal import Decimal

from data_managers.trade.subscriber import TradeManagerSubscriber
from data_managers.trade.utils import TradeMessage
from trading.market_entities.utils import Side


class ExecutionOrderFlow(TradeManagerSubscriber):
	def __init__(self):
		self.trade: TradeMessage | None = None
		self.remaining_quantity = Decimal(0)

	def process_message(self, msg: TradeMessage):
		self.trade = msg
		self.remaining_quantity = msg.quantity

	def calculate_limit_fill(
		self,
		value: Decimal,
		leverage: Decimal,
		side: Side,
		entry_price: Decimal,
	) -> tuple[Decimal, Decimal]:
		if not self.trade or self.remaining_quantity <= 0:
			return Decimal(0), Decimal(0)

		is_matching_flow = (
			(side == Side.BUY and self.trade.side == Side.SELL and self.trade.price <= entry_price)
			or (side == Side.SELL and self.trade.side == Side.BUY and self.trade.price >= entry_price)
		)
		if not is_matching_flow:
			return Decimal(0), Decimal(0)

		fill_quantity = min(
			self.remaining_quantity,
			(value * leverage) / entry_price,
		)
		self.remaining_quantity -= fill_quantity
		filled_value = (fill_quantity * entry_price) / leverage
		return entry_price, filled_value
