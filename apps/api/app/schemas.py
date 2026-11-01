from pydantic import BaseModel
from typing import Literal
class MarketRow(BaseModel):
    symbol: str
    lastPrice: float
    change24h: float
    volume24h: float
    openInterest: float | None = None
    fundingRate: float | None = None
    high24h: float | None = None
    low24h: float | None = None
    source: str = "MEXC Futures"
    updatedAt: str
    priceChange1m: float | None = None
    priceChange5m: float | None = None
    rvol5m: float | None = None
    oiChange5m: float | None = None
    cvd5m: float | None = None
class MarketResponse(BaseModel):
    source: str = "MEXC Futures"
    status: Literal["live", "degraded", "demo"]
    updatedAt: str
    items: list[MarketRow]
    warning: str | None = None
