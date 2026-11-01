# NORDVEX SCREENER PRO

A dark, multi-page market-intelligence workspace focused on MEXC Futures, with cross-exchange analytics, configurable screeners, derivatives diagnostics, narrative monitoring and ticker alerts.

## Repository layout

- `src/`: Next.js + TypeScript frontend.
- `apps/api/`: FastAPI market-data service and MEXC public adapter.
- PostgreSQL and Redis: local infrastructure declared in Docker Compose for persistence and streaming work.

## Frontend

```bash
npm install
cp .env.example .env.local
npm run dev
```

## API

```bash
cd apps/api
python -m venv .venv && source .venv/bin/activate
pip install -e '.[dev]'
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

## Implemented foundation

- Responsive dark workspace and independent pages: Overview, Crypto Bubbles, Multiple Charts, Screener Pro, Screener V1, Elite Hierarchy, Narrative Analysis, Notifications and Settings.
- Public MEXC futures ticker adapter and screener API.
- Explicit null handling for metrics that cannot yet be measured accurately.
- Initial metric integrity test.
- Environment templates and container build definitions.

## Next milestones

1. Verify live MEXC response fields and contract metadata normalization.
2. Add persistent historical candles, OI snapshots and comparable five-minute volume buckets.
3. Add trade-stream CVD and supported liquidation-event adapters.
4. Add Binance/Bybit adapters, cross-exchange basis and funding normalization.
5. Add PostgreSQL models, Redis streaming, durable alert rules and notification delivery.
6. Add backtesting, score calibration, observability and security hardening.
7. Validate production deployment before Railway is configured.

## Data integrity and security

Open interest alone does not identify whether positions are long or short. RVOL must compare equivalent historical time blocks. CVD requires aggressor-side trade classification. Liquidation clusters must be labeled estimated unless backed by observed liquidation events. Scores are not probabilities until calibrated out of sample. No trading permissions or private exchange keys are needed for public market data. Never commit secrets.

Market analytics are informational and are not financial advice.
