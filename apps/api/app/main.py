from datetime import datetime, timezone
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.exchanges.mexc import MexcPublicClient
from app.metrics import SnapshotMetrics
from app.schemas import MarketResponse
app=FastAPI(title="NORDVEX SCREENER PRO API",version="0.1.0",docs_url="/docs")
app.add_middleware(CORSMiddleware,allow_origins=settings.origins,allow_credentials=False,allow_methods=["GET"],allow_headers=["*"])
client=MexcPublicClient();metrics=SnapshotMetrics()
@app.get("/health")
async def health(): return {"status":"ok","service":"nordvex-api","time":datetime.now(timezone.utc).isoformat()}
@app.get("/api/market/screener",response_model=MarketResponse)
async def screener(limit:int=Query(100,ge=1,le=500),quote:str="USDT"):
    try:
        raw=await client.tickers();rows=[]
        for item in raw:
            row=client.normalize(item)
            if not row or (quote and not row["symbol"].endswith(quote)): continue
            rows.append(metrics.enrich(row))
        rows.sort(key=lambda x:x["volume24h"],reverse=True)
        return {"source":"MEXC Futures public contract API","status":"live","updatedAt":datetime.now(timezone.utc).isoformat(),"items":rows[:limit]}
    except Exception as exc:
        raise HTTPException(status_code=503,detail={"message":"Unable to retrieve MEXC public market data","reason":str(exc)[:240]}) from exc
