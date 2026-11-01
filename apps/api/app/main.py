import asyncio
from contextlib import asynccontextmanager, suppress
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.exchanges.mexc import MexcPublicClient
from app.metrics import SnapshotMetrics
from app.schemas import MarketResponse

client = MexcPublicClient()
metrics = SnapshotMetrics()
market_rows: list[dict] = []
last_update: str | None = None
last_error: str | None = None


async def refresh_market() -> None:
    global market_rows, last_update, last_error

    raw = await client.tickers()
    rows = []
    for item in raw:
        row = client.normalize(item)
        if not row or not row["symbol"].endswith("USDT"):
            continue
        rows.append(metrics.enrich(row))

    rows.sort(key=lambda item: item["volume24h"], reverse=True)
    market_rows = rows
    last_update = datetime.now(timezone.utc).isoformat()
    last_error = None


async def market_poller() -> None:
    global last_error

    while True:
        try:
            await refresh_market()
        except Exception as exc:
            last_error = str(exc)[:240]
        await asyncio.sleep(max(5, settings.poll_interval_seconds))


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(market_poller())
    try:
        yield
    finally:
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task


app = FastAPI(
    title="NORDVEX SCREENER PRO API",
    version="0.1.0",
    docs_url="/docs",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    is_live = bool(last_update) and last_error is None
    return {
        "status": "ok" if is_live else "degraded",
        "service": "nordvex-api",
        "marketData": "live" if is_live else "degraded",
        "lastUpdate": last_update,
        "error": last_error,
    }


@app.get("/api/market/screener", response_model=MarketResponse)
async def screener(
    limit: int = Query(100, ge=1, le=500),
    quote: str = Query("USDT", min_length=1, max_length=12),
):
    global last_error

    if not market_rows and not last_error:
        try:
            await refresh_market()
        except Exception as exc:
            last_error = str(exc)[:240]

    items = [
        row for row in market_rows
        if not quote or row["symbol"].endswith(quote.upper())
    ]
    return {
        "source": "MEXC Futures public contract API",
        "status": "live" if items and last_error is None else "degraded",
        "updatedAt": last_update or datetime.now(timezone.utc).isoformat(),
        "items": items[:limit],
        "warning": last_error,
    }


@app.get("/api/market/candles/{symbol}")
async def candles(
    symbol: str,
    interval: str = Query(
        "Min5",
        pattern="^(Min1|Min5|Min15|Min60|Hour4|Day1)$",
    ),
    limit: int = Query(200, ge=30, le=500),
):
    import re

    if not re.fullmatch(r"[A-Z0-9]+_USDT", symbol):
        raise HTTPException(
            status_code=422,
            detail="Symbol must be a valid BASE_USDT contract",
        )

    try:
        data = await client.candles(symbol, interval, limit)
        times = data.get("time", [])
        fields = ("open", "high", "low", "close", "vol", "amount")
        count = min([len(times)] + [len(data.get(key, [])) for key in fields])
        points = []
        for index in range(count):
            points.append(
                {
                    "time": int(times[index]),
                    "open": float(data["open"][index]),
                    "high": float(data["high"][index]),
                    "low": float(data["low"][index]),
                    "close": float(data["close"][index]),
                    "volume": float(data["vol"][index]),
                    "turnover": float(data["amount"][index]),
                }
            )
        return {
            "symbol": symbol,
            "interval": interval,
            "source": "MEXC Futures",
            "items": points,
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "message": "Unable to retrieve candle data",
                "reason": str(exc)[:200],
            },
        ) from exc
