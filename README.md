# NORDVEX SCREENER PRO

A dark, multi-page market-intelligence workspace with a Next.js frontend and a read-only FastAPI market-data service.

## Repository layout

- `src/`: Next.js + TypeScript frontend.
- `apps/api/`: FastAPI market-data service and MEXC public adapter.
- PostgreSQL: durable, minute-bucketed market snapshots and history.
- Docker Compose: local PostgreSQL/Redis development services.

## Local development

Start the API:

```bash
cd apps/api
python -m venv .venv && source .venv/bin/activate
pip install -e '.[dev]'
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

Start the frontend in a second terminal:

```bash
npm install
npm run dev
```

The Next.js API proxy uses `API_INTERNAL_URL` in hosted deployments and defaults to localhost for local development. For local browser requests, `src/lib/api.ts` can be configured with `NEXT_PUBLIC_API_URL=http://localhost:8000`.

## Production services

Railway is prepared as three services in the existing Crypto-Vertex project:

- `nordvex-web`: root Next.js Dockerfile.
- `nordvex-api`: FastAPI Dockerfile with root directory `apps/api`.
- `nordvex-postgres`: PostgreSQL 16 with a persistent mounted volume.

The API uses Railway's private network to connect to PostgreSQL. The web service proxies browser market-data requests to the API over the private network, so the database and API do not need public exposure. API credentials are not required for public MEXC market endpoints. Optional provider keys should be added directly to Railway variables, never committed to Git.

## Data persistence

The API creates `market_snapshots` and its time index on startup. It records one row per symbol per UTC minute, exposes `GET /api/market/history/{symbol}`, and prunes records older than `SNAPSHOT_RETENTION_DAYS` (default 30). Missing metrics remain null rather than being fabricated.

## Data integrity

- Open interest alone does not identify whether positions are long or short.
- RVOL requires comparable historical time buckets.
- CVD requires aggressor-side trade classification.
- Liquidation estimates must be distinguished from observed liquidation events.
- A score is not a calibrated probability without out-of-sample validation.

## Checks

```bash
npm run typecheck
npm run build
cd apps/api && pytest
```

Market analytics are informational. Public market data is read-only; no exchange order permissions are used.
