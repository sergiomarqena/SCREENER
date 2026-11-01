import asyncio
from contextlib import asynccontextmanager, suppress
from datetime import datetime, timezone
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.exchanges.mexc import MexcPublicClient
from app.metrics import SnapshotMetrics
from app.schemas import MarketResponse

client=MexcPublicClient()
metrics=SnapshotMetrics()
market_rows:list[dict]=[]
last_update:str|None=None
last_error:str|None=None

async def refresh_market() -> None:
    global market_rows,last_update,last_error
    raw=await client.tickers()
    rows=[]
    for item in raw:
        row=client.normalize(item)
        if not row or not row["symbol"].endswith("USDT"):
            continue
        rows.append(metrics.enrich(row))
    rows.sort(key=lambda x:x["volume24h"],reverse=True)
    market_rows=rows
    last_update=datetime.now(timezone.utc).isoformat()
    last_error=None

async def market_poller() -> None:
    global last_error
    while True:
        try:
            await refresh_market()
        except Exception as exc:
            last_error=str(exc)[:240]
        await asyncio.sleep(max(5,settings.poll_interval_seconds))

@asynccontextmanager
async def lifespan(app:FastAPI):
    task=asyncio.create_task(market_poller())
    yield
    task.cancel()
    with suppress(asyncio.CancelledError):
        await task

app=FastAPI(title="NORDVEX SCREENER PRO API",version="0.1.0",docs_url="/docs",lifespan=lifespan)
app.add_middleware(CORSMiddleware,allow_origins=settings.origins,allow_credentials=False,allow_methods=["GET"],allow_headers=["*"])

@app.get("/health")
async def health():
    return {"status":"ok","service":"nordvex-api","marketData":"live" if last_update and not last_error else "degraded","lastUpdate":last_update,"error":last_error}

@app.get("/api/market/screener",response_model=MarketResponse)
async def screener(limit:int=Query(100,ge=1,le=500),quote:str="USDT"):
    if not market_rows and not last_error:
        try:
            await refresh_market()
        except Exception as exc:
            global_error=str(exc)[:240]
            return {"source":"MEXC Futures public contract API","status":"degraded","updatedAt":datetime.now(timezone.utc).isoformat(),"items":[],"warning":global_error}
    items=[row for row in market_rows if not quote or row["symbol"].endswith(quote)]
    return {"source":"MEXC Futures public contract API","status":"live" if items else "degraded","updatedAt":last_update or datetime.now(timezone.utc).isoformat(),"items":items[:limit],"warning":last_error}
