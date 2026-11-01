# NORDVEX API

FastAPI read-only market-data service.

## Local run

```bash
cd apps/api
python -m venv .venv && source .venv/bin/activate
pip install -e '.[dev]'
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

Health: `GET /health`. Market screener: `GET /api/market/screener?limit=100`.

The first adapter reads the public MEXC Contract ticker endpoint. Intraperiod metrics remain null until enough clean snapshots exist. RVOL needs comparable historical time buckets; CVD needs aggressor-side trades. Never interpret null as zero.
