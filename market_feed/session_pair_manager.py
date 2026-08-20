from psycopg import Connection

from market_feed.utils import SessionCounter


class SessionPairManager:
    """
    Kezeli a session paireket és a feldolgozási progresszust.
    Felelős a session pairek betöltéséért és az iteráció követéséért.
    """

    def __init__(self, conn: Connection):
        self.conn = conn
        self.session_pairs = self._load_session_pairs()
        self.counter = SessionCounter(
            current=0,
            total=len(self.session_pairs)
        )

    def _load_session_pairs(self):
        """Betölti a feldolgozandó session paireket időrendi sorrendben."""
        with self.conn.cursor() as cursor:
            cursor.execute("""
                SELECT
                    sp.id,
                    sp.session_id,
                    sp.pair,
                    s.created_at
                FROM session_pairs sp
                JOIN sessions s
                    ON s.id = sp.session_id
                ORDER BY
                    s.created_at,
                    sp.id
            """)
            return cursor.fetchall()

    def get_next(self):
        """Visszaadja a következő session pairt, vagy None ha nincs több."""
        if self.counter.current >= self.counter.total:
            return None

        session_pair = self.session_pairs[self.counter.current]
        self.counter.current += 1
        return session_pair

    def has_next(self):
        """Ellenőrzi, hogy van-e további session pair."""
        return self.counter.current < self.counter.total

    def get_counter(self):
        """Visszaadja az aktuális session counter objektumot."""
        return self.counter
