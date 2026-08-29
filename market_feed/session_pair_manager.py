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
        self.session_pair_counts = self._count_pairs_by_session()
        self.counter = SessionCounter(
            session=None,
            pair=0,
            session_pair=0,
            total_sessions=len(self.session_pair_counts),
            total_pairs=0,
            total_session_pairs=len(self.session_pairs)
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

    def _count_pairs_by_session(self) -> dict[int, int]:
        counts = {}
        for _, session_id, _, _ in self.session_pairs:
            counts[session_id] = counts.get(session_id, 0) + 1
        return counts

    def get_next(self):
        """Visszaadja a következő session pairt, vagy None ha nincs több."""
        if self.counter.session_pair >= self.counter.total_session_pairs:
            return None

        session_pair = self.session_pairs[self.counter.session_pair]
        _, session_id, _, _ = session_pair

        self.counter.pair = self.counter.pair + 1 if self.counter.session == session_id else 1
        self.counter.session = session_id
        self.counter.total_pairs = self.session_pair_counts[session_id]
        self.counter.session_pair += 1
        return session_pair

    def has_next(self):
        """Ellenőrzi, hogy van-e további session pair."""
        return self.counter.session_pair < self.counter.total_session_pairs

    def get_counter(self):
        """Visszaadja az aktuális session counter objektumot."""
        return self.counter
