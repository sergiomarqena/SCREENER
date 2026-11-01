from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import asyncpg


class MarketStore:
    def __init__(self, database_url: str | None) -> None:
        self.database_url = database_url
        self.pool: asyncpg.Pool | None = None

    @property
    def enabled(self) -> bool:
        return bool(self.database_url)

    async def connect(self) -> None:
        if not self.database_url:
            return
        url = self.database_url.replace("postgresql+asyncpg://", "postgresql://", 1)
        self.pool = await asyncpg.create_pool(url, min_size=1, max_size=5, command_timeout=10)
        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS market_snapshots (
                    symbol TEXT NOT NULL,
                    bucket TIMESTAMPTZ NOT NULL,
                    price DOUBLE PRECISION NOT NULL,
                    change_24h DOUBLE PRECISION,
                    volume_24h DOUBLE PRECISION,
                    open_interest DOUBLE PRECISION,
                    funding_rate DOUBLE PRECISION,
                    high_24h DOUBLE PRECISION,
                    low_24h DOUBLE PRECISION,
                    PRIMARY KEY (symbol, bucket)
                )
            """)
            await conn.execute(
                "CREATE INDEX IF NOT EXISTS market_snapshots_bucket_idx ON market_snapshots (bucket DESC)"
            )

    async def save_snapshot(self, rows: list[dict[str, Any]]) -> None:
        if not self.pool or not rows:
            return
        now = datetime.now(timezone.utc).replace(second=0, microsecond=0)
        records = [
            (row["symbol"], now, row["price"], row.get("change24h"),
             row.get("volume24h"), row.get("openInterest"), row.get("fundingRate"),
             row.get("high24h"), row.get("low24h"))
            for row in rows
        ]
        async with self.pool.acquire() as conn:
            await conn.executemany("""
                INSERT INTO market_snapshots
                (symbol, bucket, price, change_24h, volume_24h, open_interest,
                 funding_rate, high_24h, low_24h)
                VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)
                ON CONFLICT (symbol, bucket) DO NOTHING
            """, records)

    async def history(self, symbol: str, limit: int = 1440) -> list[dict[str, Any]]:
        if not self.pool:
            return []
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT bucket, price, change_24h, volume_24h, open_interest, funding_rate
                FROM market_snapshots WHERE symbol = $1
                ORDER BY bucket DESC LIMIT $2
            """, symbol, limit)
        return [
            {"time": int(row["bucket"].timestamp()), "price": row["price"],
             "change24h": row["change_24h"], "volume24h": row["volume_24h"],
             "openInterest": row["open_interest"], "fundingRate": row["funding_rate"]}
            for row in reversed(rows)
        ]

    async def prune(self, days: int) -> None:
        if self.pool:
            cutoff = datetime.now(timezone.utc) - timedelta(days=days)
            async with self.pool.acquire() as conn:
                await conn.execute("DELETE FROM market_snapshots WHERE bucket < $1", cutoff)

    async def close(self) -> None:
        if self.pool:
            await self.pool.close()
            self.pool = None
