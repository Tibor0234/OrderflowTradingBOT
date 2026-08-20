import asyncio
import threading
from decimal import Decimal
import os

import dotenv
import psycopg

# ---- Market data & managers ----
from market_feed.feed import MarketFeed
from data_managers.open_interest.manager import OpenInterestManager
from data_managers.open_interest.subscriber import OpenInterestManagerSubscriber
from data_managers.order_book.manager import OrderBookManager
from data_managers.order_book.subscriber import OrderBookManagerSubscriber
from data_managers.trade.manager import TradeManager
from data_managers.trade.subscriber import TradeManagerSubscriber
from data_managers.context.manager import ContextManager
from data_managers.context.subscriber import ContextManagerSubscriber
from data_managers.news.manager import NewsManager
from data_managers.news.subscriber import NewsManagerSubscriber

# ---- Trading & session ----
from trading.execution.position_manager import PositionManager
from data_analysis.equity_curve.session_based import SessionBasedEquityCurve
from data_analysis.equity_curve.cumulative import CumulativeEquityCurve
from data_analysis.statistics.session_based import SessionBasedStatistics
from data_analysis.statistics.cumulative import CumulativeStatistics
from trading.execution.order_book import ExecutionOrderBook
from sessions.context import SessionContext
from strategies.core.framework import StrategyFramework

# ---- Visualization ----
from dashboard.live_dashboard import LiveDashboard
from visualizers.market_entity.trade import TradeVisualizer
from visualizers.market_entity.order import OrderVisualizer
from visualizers.data_analysis.equity_curve import EquityCurveVisualizer
from visualizers.data_analysis.statistics import StatisticsVisualizer
from visualizers.price_chart.base import PriceChartVisualizer
from visualizers.context_chart.base import ContextChartVisualizer

# ---- User config ----
from user_config import get_essentials

# ------------------- MAIN -------------------
if __name__ == "__main__":
    # ---- Essentials ----
    starting_balance, strategy, resources, visualizers = get_essentials()

    dotenv.load_dotenv()

    # ---- Dashboard ----
    dashboard = LiveDashboard('Trading dashboard')

    # ---- Equity & position management ----
    execution_order_book = ExecutionOrderBook()
    cumulative_equity_curve = CumulativeEquityCurve()
    session_based_equity_curve = SessionBasedEquityCurve()
    cumulative_statistics = CumulativeStatistics()
    session_statistics = SessionBasedStatistics()
    position_manager = PositionManager(
        starting_balance=Decimal(starting_balance),
        order_book=execution_order_book
    ) \
        .add_equity_curve(cumulative_equity_curve) \
        .add_equity_curve(session_based_equity_curve) \
        .add_statistics(cumulative_statistics) \
        .add_statistics(session_statistics)

    # ---- Session context ----
    session_context = SessionContext()

    # ---- Strategy setup ----
    strategy_framework = StrategyFramework(position_manager, session_context, execution_order_book)
    strategy.init(strategy_framework)

    # ---- Managers ----
    open_interest_manager = OpenInterestManager()
    orderbook_manager = OrderBookManager().subscribe(execution_order_book)
    trade_manager = TradeManager()
    news_manager = NewsManager()
    context_manager = ContextManager()

    # ---- DB Connection ----
    conn = psycopg.connect(os.getenv('POSTGRES_URL'))

    # ---- Market feed ----
    market_feed = MarketFeed(
        conn,
        open_interest_manager,
        orderbook_manager,
        trade_manager,
        news_manager,
        context_manager
    )

    # ---- Setup resources ----
    session_context.set_resources(resources)

    for resource in resources.values():
        if isinstance(resource, TradeManagerSubscriber):
            trade_manager.subscribe(resource)
        elif isinstance(resource, OrderBookManagerSubscriber):
            orderbook_manager.subscribe(resource)
        elif isinstance(resource, OpenInterestManagerSubscriber):
            open_interest_manager.subscribe(resource)
        elif isinstance(resource, ContextManagerSubscriber):
            context_manager.subscribe(resource)
        elif isinstance(resource, NewsManagerSubscriber):
            news_manager.subscribe(resource)

    # ---- Setup visualizers ----
    # Trade & equity visualizers
    trade_visualizer = TradeVisualizer(position_manager.trades)
    order_visualizer = OrderVisualizer(position_manager.orders, position_manager.increase_orders)
    session_equity_curve_visualizer = EquityCurveVisualizer(session_based_equity_curve)
    cumulative_equity_curve_visualizer = EquityCurveVisualizer(cumulative_equity_curve)
    session_statistics_visualizer = StatisticsVisualizer(session_statistics)
    cumulative_statistics_visualizer = StatisticsVisualizer(cumulative_statistics)

    dashboard \
        .set_execution_visualizers(trade_visualizer, order_visualizer) \
        .set_equity_curve_visualizers(session_equity_curve_visualizer, cumulative_equity_curve_visualizer) \
        .set_statistics_visualizers(session_statistics_visualizer, cumulative_statistics_visualizer) \
        .set_session_counter(market_feed.session_counter)

    # Price chart & context visualizers
    for visualizer in visualizers:
        if isinstance(visualizer, PriceChartVisualizer):
            dashboard.add_price_chart_visualizer(visualizer)
        elif isinstance(visualizer, ContextChartVisualizer):
            dashboard.add_context_chart_visualizer(visualizer)

    # ---- Start market feed in background thread ----
    threading.Thread(
        target=lambda: asyncio.run(market_feed.run()),
        daemon=True
    ).start()

    # ---- Run dashboard ----
    dashboard.run()