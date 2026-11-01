from datetime import datetime, timezone
import httpx
from app.config import settings

class MexcPublicClient:
    """Read-only MEXC Contract API client; no private/trading credentials."""
    def __init__(self) -> None:
        self.base_url = settings.mexc_base_url.rstrip("/")
    async def tickers(self) -> list[dict]:
        async with httpx.AsyncClient(timeout=8.0, headers={"User-Agent":"NORDVEX-Screener/0.1"}) as client:
            response = await client.get(f"{self.base_url}/contract/ticker")
            response.raise_for_status()
            payload = response.json()
        if not payload.get("success"):
            raise RuntimeError("MEXC ticker endpoint returned unsuccessful response")
        data = payload.get("data") or []
        return [data] if isinstance(data, dict) else data
    @staticmethod
    def normalize(item: dict) -> dict | None:
        try:
            price = float(item.get("lastPrice") or 0)
            if price <= 0: return None
            # MEXC riseFallRate is a decimal ratio. amount24 is quote turnover when supplied.
            change = float(item.get("riseFallRate") or 0) * 100
            turnover = float(item.get("amount24") or item.get("volume24") or 0)
            oi = float(item["holdVol"]) if item.get("holdVol") is not None else None
            funding = float(item["fundingRate"]) if item.get("fundingRate") is not None else None
            return {"symbol":str(item.get("symbol","")),"lastPrice":price,"change24h":change,"volume24h":turnover,"openInterest":oi,"fundingRate":funding,"high24h":float(item["high24Price"]) if item.get("high24Price") is not None else None,"low24h":float(item["lower24Price"]) if item.get("lower24Price") is not None else None,"source":"MEXC Futures","updatedAt":datetime.now(timezone.utc).isoformat(),"priceChange1m":None,"priceChange5m":None,"rvol5m":None,"oiChange5m":None,"cvd5m":None}
        except (TypeError, ValueError): return None
