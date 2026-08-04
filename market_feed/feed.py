import asyncio
from psycopg import Connection

from data_managers.context.manager import ContextManager
from data_managers.news.manager import NewsManager
from data_managers.order_book.manager import OrderBookManager
from data_managers.open_interest.manager import OpenInterestManager
from data_managers.trade.manager import TradeManager

from global_services.events.bus import EventBus
from global_services.events.utils import EventBusMsgType

from market_feed.utils import EventType, SessionCounter


class PostgresMarketFeed:

    def __init__(
        self,
        conn: Connection,
        open_interest_manager: OpenInterestManager,
        orderbook_manager: OrderBookManager,
        trade_manager: TradeManager,
        news_manager: NewsManager,
        context_manager: ContextManager,
        replay_speed=10
    ):
        self.conn = conn

        self.sleep_time = 10 ** -replay_speed

        self.open_interest_manager = open_interest_manager
        self.orderbook_manager = orderbook_manager
        self.trade_manager = trade_manager
        self.news_manager = news_manager
        self.context_manager = context_manager

        self.sessions = self.load_sessions()
        self.session_counter = SessionCounter(
            current=0,
            total=len(self.sessions)
        )


    def load_sessions(self):

        with self.conn.cursor() as cursor:

            cursor.execute("""
                SELECT id
                FROM sessions
                ORDER BY created_at
            """)

            return [
                row[0]
                for row in cursor.fetchall()
            ]


    def get_next_session(self):

        if self.session_counter.current >= self.session_counter.total:
            return None

        session = self.sessions[self.session_counter.current]

        self.session_counter.current += 1

        return session


    async def run(self):

        while True:

            session_id = self.get_next_session()

            if session_id is None:
                print("Process ended.")

                EventBus().emit(
                    EventBusMsgType.PROCESS_END
                )

                return


            print(
                "Session",
                session_id
            )

            EventBus().emit(
                EventBusMsgType.SESSION_START
            )


            sources = self.get_sources(session_id)


            while True:

                active = {
                    k: v
                    for k, v in sources.items()
                    if v["item"] is not None
                }


                if not active:
                    break


                selected_key = min(
                    active,
                    key=lambda k: self.extract_ts(
                        active[k]["item"]
                    )
                )


                item = sources[selected_key]["item"]


                self.forward_message(
                    selected_key,
                    item
                )


                try:

                    sources[selected_key]["item"] = next(
                        sources[selected_key]["generator"]
                    )

                except StopIteration:

                    sources[selected_key]["item"] = None


                await asyncio.sleep(
                    self.sleep_time
                )


    def get_sources(self, session_id):

        sources = {}


        generators = {
            EventType.TR: self.trade_generator(session_id),
            EventType.OB: self.orderbook_generator(session_id),
            EventType.OI: self.oi_generator(session_id),
            EventType.CTX: self.context_generator(session_id),
            EventType.NWS: self.news_generator(session_id),
        }


        for event_type, generator in generators.items():

            try:

                sources[event_type] = {
                    "generator": generator,
                    "item": next(generator)
                }

            except StopIteration:

                pass


        return sources



    def trade_generator(self, session_id):

        cursor = self.conn.cursor(
            name=f"trade_cursor_{session_id}"
        )


        cursor.execute("""
            SELECT raw
            FROM trades
            WHERE session_pair_id IN (
                SELECT id
                FROM session_pairs
                WHERE session_id = %s
            )
            ORDER BY timestamp
        """, (session_id,))


        for row in cursor:

            yield row[0]



    def orderbook_generator(self, session_id):

        cursor = self.conn.cursor(
            name=f"ob_cursor_{session_id}"
        )


        cursor.execute("""
            SELECT raw
            FROM orderbooks
            WHERE session_pair_id IN (
                SELECT id
                FROM session_pairs
                WHERE session_id = %s
            )
            ORDER BY timestamp
        """, (session_id,))


        for row in cursor:

            yield row[0]



    def oi_generator(self, session_id):
        return iter([])


    def context_generator(self, session_id):
        return iter([])


    def news_generator(self, session_id):
        return iter([])



    def forward_message(self, event_type, message):

        if event_type == EventType.OI:

            self.open_interest_manager.forward_message(
                message
            )

        elif event_type == EventType.OB:

            self.orderbook_manager.forward_message(
                message
            )

        elif event_type == EventType.TR:

            self.trade_manager.forward_message(
                message
            )

        elif event_type == EventType.CTX:

            self.context_manager.forward_message(
                message
            )

        elif event_type == EventType.NWS:

            self.news_manager.forward_message(
                message
            )



    def extract_ts(self, item):

        return (
            item.get("T")
            or item.get("time")
            or item.get("E")
        )