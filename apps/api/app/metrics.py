from collections import defaultdict, deque
from datetime import datetime, timezone
class SnapshotMetrics:
    """Short-lived in-memory snapshots. Missing history never becomes a fabricated zero."""
    def __init__(self, maxlen: int = 600):
        self.history = defaultdict(lambda: deque(maxlen=maxlen))
    def enrich(self, row: dict) -> dict:
        now = datetime.now(timezone.utc).timestamp()
        hist = self.history[row["symbol"]]
        hist.append({"ts":now,"price":row["lastPrice"],"oi":row.get("openInterest")})
        def pct(seconds: int):
            candidates=[x for x in hist if seconds-4 <= now-x["ts"] <= seconds+15]
            if not candidates: return None
            base=min(candidates,key=lambda x:abs((now-x["ts"])-seconds))["price"]
            return (row["lastPrice"]/base-1)*100 if base else None
        row["priceChange1m"]=pct(60)
        row["priceChange5m"]=pct(300)
        # RVOL needs historical comparable 5m time-of-day buckets; ticker volume alone is insufficient.
        row["rvol5m"]=None
        # OI delta needs a clean historical OI observation at approximately 5 minutes.
        old=[x for x in hist if x["oi"] is not None and 296 <= now-x["ts"] <= 330]
        row["oiChange5m"]=None
        if old and row.get("openInterest") is not None:
            base=min(old,key=lambda x:abs((now-x["ts"])-300))["oi"]
            if base: row["oiChange5m"]=(row["openInterest"]/base-1)*100
        # CVD requires aggressor-side trades, not ticker snapshots.
        row["cvd5m"]=None
        return row
