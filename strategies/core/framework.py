from decimal import Decimal
from session_pairs.context import SessionPairContext
from trading.market_entities.trade import Trade
from trading.execution.position_manager import PositionManager
from trading.market_entities.order import Order, MarketOrder, LimitOrder
from trading.market_entities.stop_order import StopOrder, TakeProfit, StopLoss, ReduceOnly
from trading.market_entities.increase_order import IncreaseOrder, IncreaseLimitOrder, IncreaseMarketOrder
from strategies.core.sequence_analyzers import SequenceAnalyzers
from trading.execution.order_book import ExecutionOrderBook
from trading.market_entities.utils import OrderType, Side
from global_services.data.provider import DataProvider
from analyzers.ohlcv_timeframe.model import OHLCVTimeframe
from analyzers.ohlcv_volume_profile.model import OHLCVVolumeProfile
from analyzers.microprice_deviation.model import MicropriceDeviation
from analyzers.open_interest.model import OpenInterest
from analyzers.order_book_imbalance.model import OrderBookImbalance
from analyzers.timeframe.model import Timeframe
from analyzers.volume_delta.model import VolumeDelta
from analyzers.volume_profile.model import VolumeProfile
from analyzers.big_trades.model import BigTrades

class StrategyFramework(SequenceAnalyzers):
    def __init__(self, position_manager: PositionManager, session_pair_context: SessionPairContext, execution_order_book: ExecutionOrderBook):
        self.position_manager = position_manager
        self.session_pair_context = session_pair_context
        self.order_book = execution_order_book

        self.orders = position_manager.orders
        self.trades = position_manager.trades

    # place orders

    def place_limit_order(self, side, value, entry_price, leverage, kill=None, kill_after_fill=None):
        order = LimitOrder(
            side=Side(side),
            value=value,
            entry_price=entry_price,
            leverage=leverage,
            kill=kill * 1000 if kill is not None else None,
            kill_after_fill=kill_after_fill * 1000 if kill_after_fill is not None else None
        )
        self.position_manager.place_order(order)
        return order
    
    def place_market_order(self, side, value, leverage):
        order = MarketOrder(
            side=Side(side),
            value=value,
            leverage=leverage
        )
        self.position_manager.place_order(order)
        return order
    
    def place_increase_limit_order(self, source: Order | Trade, value, entry_price, leverage, kill_after_fill=None):
        order = IncreaseLimitOrder(
            value=value,
            entry_price=entry_price,
            leverage=leverage,
            kill_after_fill=kill_after_fill * 1000 if kill_after_fill is not None else None
        )
        source.link(order)
        self.position_manager.place_order(order)
        return order
    
    def place_increase_marker_order(self, source: Order | Trade, value, leverage):
        order = IncreaseMarketOrder(
            value=value,
            leverage=leverage
        )
        source.link(order)
        self.position_manager.place_order(order)
        return order
    
    def place_take_profit_limit(self, source: Order | Trade, price, pct):
        order = TakeProfit(
            price=price,
            type=OrderType.LIMIT,
            pct=pct
        )
        source.link(order)
        self.position_manager.place_order(order)
        return order
    
    def place_take_profit_market(self, source: Order | Trade, price, pct):
        order = TakeProfit(
            price=price,
            type=OrderType.MARKET,
            pct=pct
        )
        source.link(order)
        self.position_manager.place_order(order)
        return order
    
    def place_stop_loss(self, source: Order | Trade, price):
        order = StopLoss(
            price=price
        )
        source.link(order)
        self.position_manager.place_order(order)
        return order
    
    def place_reduce_only_order(self, source: Order | Trade, pct):
        order = ReduceOnly(
            pct=pct
        )
        source.link(order)
        self.position_manager.place_order(order)
        return order

    # position manager actions

    def cancel_order(self, order: Order | IncreaseOrder | StopOrder):
        self.position_manager.cancel_order(order)

    def trail_stop_loss(self, trade: Trade, price):
        sl = self.get_next_stop_loss(trade)
        if sl: 
            sl.price = Decimal(price)
        else:
            sl_order = StopLoss(Decimal(price))
            trade.link(sl_order)
            self.position_manager.place_order(sl_order)
    
    # execuiton queries

    def is_trade_open(self):
        return len(self.position_manager.trades) > 0
    
    def is_order_pending(self):
        return len(self.position_manager.orders) + len(self.position_manager.increase_orders) > 0
    
    def get_trades(self):
        return self.position_manager.trades.copy()
    
    def get_orders(self):
        return self.position_manager.orders.copy()
    
    def get_increase_orders(self, source: Order | Trade):
        return [o for o in self.position_manager.increase_orders if o.source_id == source.id]
    
    def get_stop_orders(self, source: Order | Trade):
        return [o for o in self.position_manager.stop_orders if o.source_id == source.id]
    
    def get_take_profits(self, source: Order | Trade):
        return [o for o in self.get_stop_orders(source) if isinstance(o, TakeProfit)]
    
    def get_stop_losses(self, source: Order | Trade):
        return [o for o in self.get_stop_orders(source) if isinstance(o, StopLoss)]

    def get_next_trade(self):
        return next((t for t in self.get_trades()), None)
    
    def get_next_order(self):
        return next((t for t in self.get_orders()), None)
    
    def get_next_increase_order(self, source: Order | Trade):
        return next((t for t in self.get_increase_orders(source)), None)
    
    def get_next_take_profit(self, source: Order | Trade):
        return next((t for t in self.get_take_profits(source)), None)
    
    def get_next_stop_loss(self, source: Order | Trade):
        return next((t for t in self.get_stop_losses(source)), None)

    # order book queries

    def get_best_bid(self):
        return self.order_book.best_bid
    
    def get_best_ask(self):
        return self.order_book.best_ask

    def get_spread(self):
        return self.order_book.spread

    # data provider queries

    def get_current_symbol(self):
        return DataProvider().get_symbol()

    def get_current_price(self):
        return DataProvider().get_price()
    
    def get_current_time(self):
        return DataProvider().get_time()

    # session context queries

    def get_price_distance(self, ticks: int | Decimal) -> Decimal:
        """Returns an instrument-independent price distance in ticks."""
        metadata = self.session_pair_context.get_instrument_metadata()

        return Decimal(str(ticks)) * metadata.tick_size

    # resource queries

    def get_ohlcv_timeframe(self, name: str) -> OHLCVTimeframe:
        return self.session_pair_context.get_resource(name)

    def get_ohlcv_volume_profile(self, name: str) -> OHLCVVolumeProfile:
        return self.session_pair_context.get_resource(name)

    def get_microprice_deviation(self, name: str) -> MicropriceDeviation:
        return self.session_pair_context.get_resource(name)

    def get_open_interest(self, name: str) -> OpenInterest:
        return self.session_pair_context.get_resource(name)

    def get_order_book_imbalance(self, name: str) -> OrderBookImbalance:
        return self.session_pair_context.get_resource(name)

    def get_timeframe(self, name: str) -> Timeframe:
        return self.session_pair_context.get_resource(name)

    def get_volume_delta(self, name: str) -> VolumeDelta:
        return self.session_pair_context.get_resource(name)

    def get_volume_profile(self, name: str) -> VolumeProfile:
        return self.session_pair_context.get_resource(name)

    def get_big_trades(self, name: str) -> BigTrades:
        return self.session_pair_context.get_resource(name)