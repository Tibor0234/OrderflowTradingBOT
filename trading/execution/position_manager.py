from decimal import Decimal
from trading.market_entities.order import Order
from trading.market_entities.stop_order import StopOrder, ReduceOnly, LiquidationOrder
from trading.market_entities.increase_order import IncreaseOrder
from trading.market_entities.trade import Trade
from global_services.events.bus import EventBus
from global_services.events.utils import EventBusMsgType
from trading.execution.order_book import ExecutionOrderBook
from data_analysis.equity_curve.base import BaseEquityCurve
from data_analysis.statistics.base import BaseStatistics
from trading.market_entities.utils import OrderType

class PositionManager:
    def __init__(self, starting_balance, order_book: ExecutionOrderBook, maker_fee_pct=0.02, taker_fee_pct=0.06):
        self.starting_balance = Decimal(starting_balance)
        self.order_book = order_book

        self.maker_fee_rate = Decimal(maker_fee_pct / 100)
        self.taker_fee_rate = Decimal(taker_fee_pct / 100)

        self.trades: list[Trade] = []
        self.orders: list[Order] = []
        self.increase_orders: list[IncreaseOrder] = []
        self.stop_orders: list[StopOrder] = []

        self.realized_balance = self.starting_balance

        self.equity_curves: list[BaseEquityCurve] = []
        self.statistics: list[BaseStatistics] = []
        
        EventBus().subscribe(EventBusMsgType.PRICE_UPDATE, self.on_price_update)
        EventBus().subscribe(EventBusMsgType.SESSION_START, self.on_session_start)
        EventBus().subscribe(EventBusMsgType.PROCESS_END, self.clear_state)

    @property
    def floating_balance(self):
        return sum(t.floating_pnl for t in self.trades)
    
    @property
    def total_balance(self):
        return self.realized_balance + self.floating_balance

    # ------------------------
    # ⚠️ Execution Management
    # ------------------------

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

            for st in self.statistics:
                st.update_on_trade_close(trade)

        self.increase_orders = [o for o in self.increase_orders if o.source_id != trade.id]
        self.stop_orders = [o for o in self.stop_orders if o.source_id != trade.id]

    def _finalize_order(self, order: Order):
        if order in self.orders:
            self.orders.remove(order)

        self.increase_orders = [o for o in self.increase_orders if o.source_id != order.id]
        self.stop_orders = [o for o in self.stop_orders if o.source_id != order.id]

    def _link_order_to_trade(self, order: Order, trade: Trade) -> IncreaseOrder:
        increase_order = order.convert_to_increase_order()
        self.orders.remove(order)
        trade.link(increase_order)
        self.increase_orders.append(increase_order)
        return increase_order

    # ---------------- ORDER FILL ----------------

    def on_order_triggered(self, order: Order | IncreaseOrder):
        is_limit = order.type == OrderType.LIMIT

        if is_limit:
            execution_price, filled_value = self.order_book.calculate_limit_fill(
                order.value, order.side, order.entry_price
            )

            if filled_value == Decimal(0):
                return

            fee_rate = self.maker_fee_rate
        else:
            execution_price = self.order_book.calculate_market_fill(
                order.value, order.side
            )
            filled_value = order.value
            fee_rate = self.taker_fee_rate

        if isinstance(order, IncreaseOrder):
            trade = self._get_trade(order)
            if not trade:
                return

            if order.side != trade.side:
                raise ValueError("Cannot add opposite side order to existing trade")

            trade.update_on_fill(execution_price, filled_value, order.leverage)
            trade.charge_fee_from_value(filled_value, fee_rate)
        else:
            trade = Trade.convert_from_order(order, execution_price, filled_value)
            # order -> increase order
            order = self._link_order_to_trade(order, trade)
            trade.charge_fee(fee_rate)
            self.trades.append(trade)

        self._set_liquidation_order(trade)

        order.value -= filled_value
        if order.is_filled():
            self.increase_orders.remove(order)
        else:
            order.on_partial_fill()


    # ---------------- STOP FILL ----------------

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
                entry_price=stop_order.price
            )

            if filled_value == Decimal(0):
                return

            filled_close_rate = (filled_value / order_value) * stop_order.close_rate
            fee_value = filled_value
            fee_rate = self.maker_fee_rate
        else:
            execution_price = self.order_book.calculate_market_fill(
                value=order_value,
                side=stop_order.side
            )
            filled_close_rate = stop_order.close_rate
            fee_value = order_value
            fee_rate = self.taker_fee_rate

        # fee + close
        trade.charge_fee_from_value(fee_value, fee_rate)
        closed_value, realized = trade.close_trade_partial(execution_price, filled_close_rate)
        self.realized_balance += closed_value + realized

        # stop order frissítés
        stop_order.close_rate -= filled_close_rate
        if stop_order.is_filled():
            self.stop_orders.remove(stop_order)

        # trade lezárás ha kell
        if not trade.is_active():
            self._finalize_trade(trade)

    # ------------------------
    # ⚠️ Position Management
    # ------------------------

    def place_order(self, order: Order | IncreaseOrder | StopOrder):
        if isinstance(order, Order):
            order.place()
            self.orders.append(order)
        elif isinstance(order, IncreaseOrder):
            self.increase_orders.append(order)
        else:
            self.stop_orders.append(order)

    def cancel_order(self, order: Order | IncreaseOrder | StopOrder):
        if isinstance(order, Order):
            self._finalize_order(order)
        else:
            if order in self.increase_orders:
                self.increase_orders.remove(order)
            elif order in self.stop_orders:
                self.stop_orders.remove(order)

    def on_price_update(self):
        for order in self.orders.copy():
            if order.is_killed():
                self._finalize_order(order)

            elif order.is_triggered():
                self.on_order_triggered(order)
        
        if self.trades:
            for linked_order in self.increase_orders.copy() + self.stop_orders.copy():
                if linked_order.is_triggered() and self._is_source_open(linked_order):
                    if isinstance(linked_order, IncreaseOrder):
                        self.on_order_triggered(linked_order)
                    else:
                        self.on_stop_order_triggered(linked_order)

            for eq in self.equity_curves:
                eq.update(self.total_balance)
            
            for st in self.statistics:
                st.update_on_price_change(self.total_balance)
        
        else:
            for eq in self.equity_curves:
                if not eq.is_initialized():
                    eq.update(self.total_balance)

    def on_session_start(self):
        self.clear_state()

        for eq in self.equity_curves:
            eq.start_session()
        
        for st in self.statistics:
            st.session_start(self.total_balance)
    
    def clear_state(self):
        for trade in self.trades:
            stop_order = ReduceOnly(pct=100)
            self.stop_orders.append(stop_order)
            trade.link(stop_order)
            self.on_stop_order_triggered(stop_order)

        self.orders.clear()
        self.increase_orders.clear()
        self.stop_orders.clear()
        self.trades.clear()

    # ------------------------
    # ⚠️ Statistics
    # ------------------------

    def add_equity_curve(self, equity_curve: BaseEquityCurve):
        self.equity_curves.append(equity_curve)
        return self

    def add_statistics(self, statistics: BaseStatistics):
        self.statistics.append(statistics)
        return self