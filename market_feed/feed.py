from psycopg import Connection

from data_managers.context.manager import ContextManager
from data_managers.news.manager import NewsManager
from data_managers.order_book.manager import OrderBookManager
from data_managers.open_interest.manager import OpenInterestManager
from data_managers.trade.manager import TradeManager

from global_services.events.bus import EventBus
from global_services.events.utils import EventBusMsgType

from market_feed.session_pair_manager import SessionPairManager
from market_feed.database_generator_factory import DatabaseGeneratorFactory
from market_feed.source_coordinator import SourceCoordinator
from market_feed.event_forwarder import EventForwarder
from sessions.utils import InstrumentMetadata


class MarketFeed:
    """
    Egy Postgres adatbázisból történő market feed replay.
    
    Koordinálja a session paireket, adatforrásokat és az event forwarding-ot.
    
    A replay egysége egy session_pair:
      - session 1 -> BTC
      - session 1 -> ETH
      - session 2 -> BTC
      - session 2 -> ETH
    
    Ezek egymás után kerülnek feldolgozásra.
    """

    def __init__(
        self,
        conn: Connection,
        open_interest_manager: OpenInterestManager,
        orderbook_manager: OrderBookManager,
        trade_manager: TradeManager,
        news_manager: NewsManager,
        context_manager: ContextManager
    ):
        self.session_pair_manager = SessionPairManager(conn)
        
        self.database_generator_factory = DatabaseGeneratorFactory(conn)
        self.source_coordinator = SourceCoordinator(
            self.database_generator_factory
        )
        
        self.event_forwarder = EventForwarder(
            open_interest_manager,
            orderbook_manager,
            trade_manager,
            context_manager,
            news_manager,
        )

    @property
    def session_counter(self):
        """
        Hozzáférést biztosít a session counter objektumhoz a dashboard számára.
        
        Visszaadja a SessionCounter objektumot, amely tartalmazza:
        - current: aktuális session pár indexe (0-based)
        - total: összes session pár száma
        
        Használat:
            current = market_feed.session_counter.current
            total = market_feed.session_counter.total
        """
        return self.session_pair_manager.get_counter()

    async def run(self):
        """
        Főprogram: iterálja az összes session pairt és streameli az adatokat.
        """
        while True:
            session_pair = self.session_pair_manager.get_next()

            if session_pair is None:
                print("Process ended.")
                EventBus().emit(EventBusMsgType.PROCESS_END)
                return

            await self._replay_session_pair(session_pair)

    async def _replay_session_pair(self, session_pair):
        """Egy session pair összes adatát replaye."""
        session_pair_id, session_id, pair, created_at = session_pair

        print(
            pair.upper(),
            "session pair",
            session_pair_id,
            "| session",
            session_id
        )

        metadata_row = self.database_generator_factory.instrument_metadata(
            session_pair_id
        )
        instrument_metadata = (
            InstrumentMetadata(*metadata_row)
            if metadata_row is not None
            else None
        )
        EventBus().emit(EventBusMsgType.SESSION_START)
        EventBus().emit(
            EventBusMsgType.SESSION_METADATA,
            instrument_metadata=instrument_metadata
        )

        sources = self.source_coordinator.initialize_sources(session_pair_id)

        while True:
            active_sources = self.source_coordinator.get_active_sources(sources)

            if not active_sources:
                break

            selected_event_type = self.source_coordinator.select_next_source(
                active_sources
            )

            item = sources[selected_event_type]["item"]

            self.event_forwarder.forward(selected_event_type, item)

            self.source_coordinator.advance_source(sources, selected_event_type)

        EventBus().emit(EventBusMsgType.SESSION_END)