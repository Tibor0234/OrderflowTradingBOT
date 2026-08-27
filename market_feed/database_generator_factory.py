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
        Egy session_pair context candle-jeit fetch csomagok szerint
        streameli. A csomagok sorrendjét a fetch timestampje határozza meg.

        Egy yield egy teljes context csomag, amelyet a ContextManager
        közvetlenül fel tud dolgozni.
        """
        cursor = self.conn.cursor(
            name=f"context_cursor_{session_pair_id}"
        )
        try:
            cursor.execute("""
                SELECT
                    fetch.id,
                    fetch.interval,
                    fetch.period,
                    fetch.timestamp,
                    candle.open_time,
                    candle.raw
                FROM ohlcv_fetches AS fetch
                JOIN ohlcv AS candle
                    ON candle.fetch_id = fetch.id
                WHERE fetch.session_pair_id = %s
                ORDER BY fetch.timestamp, candle.open_time
            """, (session_pair_id,))

            fetches = {}
            for (
                fetch_id,
                interval,
                period,
                fetch_timestamp,
                open_time,
                raw_candle,
            ) in cursor:
                fetch = fetches.setdefault(
                    fetch_id,
                    {
                        "interval": interval,
                        "period": period,
                        "timestamp": fetch_timestamp,
                        "candles": [],
                    },
                )
                fetch["candles"].append((open_time, raw_candle))

            packages = []
            for fetch in fetches.values():
                candles = [
                    raw_candle
                    for _, raw_candle in sorted(
                        fetch["candles"],
                        key=lambda candle: candle[0],
                    )
                ]
                packages.append({
                    "period": fetch["period"],
                    "interval": fetch["interval"],
                    "open_time": int(candles[0]["open_time"]),
                    "candles": candles,
                    "fetch_timestamp": fetch["timestamp"],
                })

            for package in sorted(
                packages,
                key=lambda package: package["fetch_timestamp"]
            ):
                yield package
        finally:
            cursor.close()

    def news_generator(self, session_pair_id):
        """News adatait streameli (jelenleg üres)."""
        return iter([])
