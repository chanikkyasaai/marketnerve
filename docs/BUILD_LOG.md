# Build Log

## 2026-03-23

- Read and decomposed the MarketNerve product PDF into a greenfield implementation plan.
- Established a monorepo structure for `apps/web`, `backend`, shared config, and docs.
- Added shared seeded market-intelligence data to support deterministic product development.
- Implemented backend domain services and API surfaces for signals, patterns, portfolio, stories, IPOs, audit, and health.
- Built the first end-to-end frontend experience covering the core product routes from the PDF.
- Added dedicated test folders for backend and frontend logic.
- Added environment templates for future live data, auth, and LLM provider keys.
- Upgraded the frontend to a patched Next.js 15.5.14 release and verified a production build.
- Replaced purely static frontend rendering with backend-aware loaders and resilient fallbacks.
- Added interactive Portfolio Lens analysis and Q&A flows wired to backend endpoints.
- Added filtering/search flows for signals, patterns, and story arcs.
- Expanded the backend into richer domain services with subscriptions, websocket event streams, enriched signal/pattern responses, and deeper portfolio analytics.
- Moved the backend transport layer into explicit API router and websocket modules under `backend/app/api`.
