from market_feed.utils import EventType
from market_feed.database_generator_factory import DatabaseGeneratorFactory
from market_feed.message_extractor import MessageExtractor


class SourceCoordinator:
    """
    Kezeli az aktív adatforrásokat és azok állapotát.
    Összehangol több generátort timestamp alapján.
    """

    def __init__(self, generator_factory: DatabaseGeneratorFactory):
        self.generator_factory = generator_factory
        self.extractor = MessageExtractor()

    def initialize_sources(self, session_pair_id):
        """
        Inicializálja az összes adatforrást egy session pair-hez.
        
        Visszaad egy dictionary-t a forrásokról, amely tartalmazza
        a generátort és az első elemet.
        """
        sources = {}
        generator_methods = {
            EventType.TR: self.generator_factory.trade_generator,
            EventType.OB: self.generator_factory.orderbook_generator,
            EventType.OI: self.generator_factory.oi_generator,
            EventType.CTX: self.generator_factory.context_generator,
            EventType.NWS: self.generator_factory.news_generator,
        }

        for event_type, method in generator_methods.items():
            generator = method(session_pair_id)
            try:
                sources[event_type] = {
                    "generator": generator,
                    "item": next(generator)
                }
            except StopIteration:
                pass

        return sources

    def get_active_sources(self, sources):
        """Csak azokat a forrásokat adja vissza, amelyeknek van itemjük."""
        return {
            event_type: source
            for event_type, source in sources.items()
            if source["item"] is not None
        }

    def select_next_source(self, active_sources):
        """
        Kiválasztja azt a forrást, amely a legkisebb timestampű itemet tartalmazza.
        
        A replay timestamp alapján koordinált.
        """
        if not active_sources:
            return None

        return min(
            active_sources,
            key=lambda event_type: self.extractor.extract_timestamp(
                active_sources[event_type]["item"]
            )
        )

    def advance_source(self, sources, event_type):
        """Egy forrást előrelépteti a következő elemre."""
        try:
            sources[event_type]["item"] = next(
                sources[event_type]["generator"]
            )
        except StopIteration:
            sources[event_type]["item"] = None
