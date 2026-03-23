# MarketNerve Architecture

## Product slices

- Signal Scout: ranked, source-cited market signals with anomaly and back-test metadata.
- Pattern Mind: technical-pattern summaries with ticker-specific historical context.
- Portfolio Lens: upload parsing, portfolio x-ray, and source-cited Q&A over holdings.
- Story Engine: daily wrap media objects plus story-arc timelines.
- IPO Intelligence: active IPO cards with retail-friendly summaries.
- Audit Trail: every surfaced signal exposes the decision context.

## Runtime shape

- `apps/web` is the experience layer. It renders the home feed, deep-dive pages, and audit views.
- `backend` is the intelligence layer. It reads the shared seed dataset, exposes APIs and websocket streams, computes derived portfolio metrics, and enriches module outputs into product-grade response shapes.
- `config/marketnerve.seed.json` is the current source of truth for demo-mode content so both stacks remain consistent.

## Backend layout

- `backend/app/api/routes`: HTTP route modules grouped by product area.
- `backend/app/api/websockets`: live stream endpoints for signals, patterns, and filings.
- `backend/app/services`: business logic and intelligence enrichment.
- `backend/app/data`: repository and seed access.
- `backend/app/models`: shared request and response schemas.

## Engineering choices

- Shared seed data keeps the build deterministic and testable before live market integrations are introduced.
- Backend services are organized by domain instead of by transport, which makes later migration to queues, workers, or LangGraph agents easier.
- A repository layer now separates seed access from intelligence logic so live data adapters can replace the current demo source cleanly.
- Frontend fetches from the backend when available and falls back to the seed dataset for resilience during demo or offline development.
- Portfolio calculations are deterministic and verified in tests because hallucinated financial figures are the highest-risk failure mode in the product doc.

## Live integration path

The repository is structured so the following upgrades can slot in without major rewrites:

- Replace seed readers with adapters for NSE/BSE filings, OHLCV feeds, and ET data.
- Introduce a queue/event bus between ingestion, enrichment, and publishing.
- Swap the rule-based portfolio Q&A synthesizer with an LLM orchestration layer once API keys are provided.
- Persist signals, audits, and stories to PostgreSQL/Redis instead of memory-backed seed snapshots.
