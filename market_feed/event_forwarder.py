from data_managers.ohlcv.manager import OHLCVManager
from data_managers.news.manager import NewsManager
from data_managers.order_book.manager import OrderBookManager
from data_managers.open_interest.manager import OpenInterestManager
from data_managers.trade.manager import TradeManager

from market_feed.utils import EventType


class EventForwarder:
    """
    Üzenetek irányítása a megfelelő manager felé event_type alapján.
    """

    def __init__(
        self,
        open_interest_manager: OpenInterestManager,
        orderbook_manager: OrderBookManager,
        trade_manager: TradeManager,
        ohlcv_manager: OHLCVManager,
        news_manager: NewsManager,
    ):
        self.managers = {
            EventType.OI: open_interest_manager,
            EventType.OB: orderbook_manager,
            EventType.TR: trade_manager,
            EventType.OHLCV: ohlcv_manager,
            EventType.NWS: news_manager,
        }

    def forward(self, event_type, message):
        """Üzenet továbbítása a megfelelő managernek."""
        manager = self.managers.get(event_type)
        if manager:
            manager.forward_message(message)
