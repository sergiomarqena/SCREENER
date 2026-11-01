# NORDVEX SCREENER PRO

A market-intelligence workspace focused on MEXC Futures, with cross-exchange context, configurable screeners, derivatives analytics, narrative monitoring and user-defined alerts.

## Product principles

- Data provenance is explicit: every metric records its source, timestamp and freshness.
- Scores are analytical scores, not claims of guaranteed returns or calibrated win probabilities.
- Missing or unsupported exchange metrics are shown as unavailable, never silently fabricated.
- Exchange credentials remain server-side and are never exposed to the browser.
- The application is read-only in its initial release; no order execution or trading keys are required.

## Planned architecture

- `apps/web`: Next.js, TypeScript, Tailwind CSS and TradingView Lightweight Charts.
- `apps/api`: FastAPI service, exchange adapters, metric calculations and WebSocket delivery.
- `packages/contracts`: shared API/data contracts.
- PostgreSQL: durable user settings, watchlists, alert rules and metric snapshots.
- Redis: short-lived market state, pub/sub and rate-limit coordination.

## Pages

Overview, Crypto Bubbles, Multiple Charts, Screener Pro, Screener V1, Elite Hierarchy, Narrative Analysis, Notifications and Settings.

## Development

The repository is being initialized in stages. Railway deployment is intentionally deferred until implementation, data validation, tests and security checks are complete.

### Safety and data integrity

Market indicators are informational tools, not financial advice. Open interest does not independently identify whether new positions are long or short. CVD requires trade-side classification from exchange trade streams. Liquidation density must be labeled as estimated unless backed by actual liquidation data. Directional scores must not be represented as probabilities until calibrated against out-of-sample historical results.

## Configuration

Copy the relevant `.env.example` files to local environment files. Never commit API secrets, private keys, access tokens or production credentials.
