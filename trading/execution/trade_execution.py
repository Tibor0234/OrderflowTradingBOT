from decimal import Decimal

from trading.market_entities.increase_order import IncreaseOrder
from trading.market_entities.stop_order import LiquidationOrder, ReduceOnly, StopOrder
from trading.market_entities.trade import Trade
from trading.market_entities.utils import OrderType
from global_services.events.bus import EventBus
from global_services.events.utils import EventBusMsgType


class TradeExecutionManager:
    def __init__(self, position_manager):
        self.position_manager = position_manager

    @property
    def trades(self):
        return self.position_manager.trades

    @property
    def increase_orders(self):
        return self.position_manager.increase_orders

    @property
    def stop_orders(self):
        return self.position_manager.stop_orders

    @property
    def order_book(self):
        return self.position_manager.order_book

    @property
    def maker_fee_rate(self):
        return self.position_manager.maker_fee_rate

    @property
    def taker_fee_rate(self):
        return self.position_manager.taker_fee_rate

    def _set_liquidation_order(self, trade: Trade):
        liq_price = trade.execution_price - (trade.side.value * (trade.execution_price / trade.leverage))
        for linked_order in self.stop_orders:
            if isinstance(linked_order, LiquidationOrder) and linked_order.source_id == trade.id:
                linked_order.price = liq_price
                break
        else:
            liq_order = LiquidationOrder(liq_price)
            trade.link(liq_order)
            self.stop_orders.append(liq_order)

    def _get_trade(self, linked_order: IncreaseOrder | StopOrder):
        return next((t for t in self.trades if t.id == linked_order.source_id), None)

    def _is_source_open(self, linked_order: IncreaseOrder | StopOrder):
        return self._get_trade(linked_order) is not None

    def _finalize_trade(self, trade: Trade):
        if trade in self.trades:
            trade.close_trade()
            self.trades.remove(trade)
            EventBus().emit(EventBusMsgType.TRADE_CLOSE, trade)

            for st in self.position_manager.statistics:
                st.update_on_trade_close(trade)

        self.increase_orders[:] = [o for o in self.increase_orders if o.source_id != trade.id]
        self.stop_orders[:] = [o for o in self.stop_orders if o.source_id != trade.id]

    def on_stop_order_triggered(self, stop_order: StopOrder):
        trade = self._get_trade(stop_order)
        if not trade:
            return

        is_limit = stop_order.type == OrderType.LIMIT
        order_value = trade.value * stop_order.close_rate

        if is_limit:
            execution_price, filled_value = self.order_book.calculate_limit_fill(
                value=order_value,
                side=stop_order.side,
                entry_price=stop_order.price,
            )

            if filled_value == Decimal(0):
                return

            filled_close_rate = (filled_value / order_value) * stop_order.close_rate
            fee_value = filled_value
            fee_rate = self.maker_fee_rate
        else:
            execution_price = self.order_book.calculate_market_fill(
                value=order_value,
                side=stop_order.side,
            )
            filled_close_rate = stop_order.close_rate
            fee_value = order_value
            fee_rate = self.taker_fee_rate

        trade.update_metadata(stop_order.metadata)
        trade.charge_fee_from_value(fee_value, fee_rate)
        closed_value, realized = trade.close_trade_partial(execution_price, filled_close_rate)
        self.position_manager.realized_balance += closed_value + realized

        stop_order.close_rate -= filled_close_rate
        if stop_order.is_filled():
            self.stop_orders.remove(stop_order)

        if not trade.is_active():
            self._finalize_trade(trade)

    def close_expired_trades(self):
        for trade in list(self.trades):
            stop_order = ReduceOnly(pct=100)
            self.stop_orders.append(stop_order)
            trade.link(stop_order)
            self.on_stop_order_triggered(stop_order)
