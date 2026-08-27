from psycopg import Connection


class DatabaseGeneratorFactory:
    """
    Factory a különböző adatforrásokból történő generátorok létrehozásához.
    """

    def __init__(self, conn: Connection):
        self.conn = conn

    def instrument_metadata(self, session_pair_id):
        """Betölti egy session pair instrumentumának metadata adatait."""
        with self.conn.cursor() as cursor:
            cursor.execute("""
                SELECT
                    session_pair_id,
                    symbol,
                    status,
                    base_asset,
                    quote_asset,
                    contract_type,
                    tick_size,
                    quantity_step,
                    price_precision,
                    quantity_precision,
                    min_quantity,
                    min_notional,
                    onboard_date
                FROM instrument_metadata
                WHERE session_pair_id = %s
            """, (session_pair_id,))
            return cursor.fetchone()

    def trade_generator(self, session_pair_id):
        """
        Egyetlen session_pair trade adatait streameli.

        FONTOS:
        Itt már közvetlenül session_pair_id alapján szűrünk,
        tehát nem kerülhetnek bele ugyanazon session más pairei.
        """
        cursor = self.conn.cursor(
            name=f"trade_cursor_{session_pair_id}"
        )
        cursor.itersize = 5000
        try:
            cursor.execute("""
                SELECT raw
                FROM trades
                WHERE session_pair_id = %s
                ORDER BY timestamp
            """, (session_pair_id,))
            for row in cursor:
                yield row[0]
        finally:
            cursor.close()

    def orderbook_generator(self, session_pair_id):
        """Egyetlen session_pair orderbook adatait streameli."""
        cursor = self.conn.cursor(
            name=f"ob_cursor_{session_pair_id}"
        )
        cursor.itersize = 2000
        try:
            cursor.execute("""
                SELECT raw
                FROM orderbooks
                WHERE session_pair_id = %s
                ORDER BY timestamp
            """, (session_pair_id,))
            for row in cursor:
                yield row[0]
        finally:
            cursor.close()

    def oi_generator(self, session_pair_id):
        """Open interest adatait streameli."""
        cursor = self.conn.cursor(
            name=f"oi_cursor_{session_pair_id}"
        )
        cursor.itersize = 100
        try:
            cursor.execute("""
                SELECT raw
                FROM open_interest
                WHERE session_pair_id = %s
                ORDER BY timestamp
            """, (session_pair_id,))
            for row in cursor:
                yield row[0]
        finally:
            cursor.close()

    def context_generator(self, session_pair_id):
        """
        Egy session_pair context candle-jeit period és interval szerint
        csoportosítva streameli.

        Egy yield egy teljes context csomag, amelyet a ContextManager
        közvetlenül fel tud dolgozni.
        """
        cursor = self.conn.cursor(
            name=f"context_cursor_{session_pair_id}"
        )
        try:
            cursor.execute("""
                SELECT period, "interval", raw
                FROM ohlcv
                WHERE session_pair_id = %s
            """, (session_pair_id,))

            grouped_candles = {}
            for period, interval, raw_candle in cursor:
                key = (period, interval)
                grouped_candles.setdefault(key, []).append(raw_candle)

            packages = []
            for (period, interval), candles in grouped_candles.items():
                candles.sort(key=lambda candle: int(candle["open_time"]))
                packages.append({
                    "period": period,
                    "interval": interval,
                    "open_time": int(candles[0]["open_time"]),
                    "candles": candles
                })

            for package in sorted(
                packages,
                key=lambda package: package["open_time"]
            ):
                yield package
        finally:
            cursor.close()

    def news_generator(self, session_pair_id):
        """News adatait streameli (jelenleg üres)."""
        return iter([])
