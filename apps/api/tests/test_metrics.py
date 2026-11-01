from app.metrics import SnapshotMetrics
def test_intraperiod_metrics_are_not_fabricated():
    result=SnapshotMetrics().enrich({"symbol":"BTC_USDT","lastPrice":60000.0,"openInterest":100.0,"volume24h":1000000.0})
    assert result["priceChange1m"] is None
    assert result["priceChange5m"] is None
    assert result["rvol5m"] is None
    assert result["cvd5m"] is None
