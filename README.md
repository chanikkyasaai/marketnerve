# MarketNerve

MarketNerve is an AI intelligence layer for Indian retail investors.
It turns noisy market data into actionable decisions across signals, chart patterns, portfolio diagnostics, narrative intelligence, and IPO tracking.

## Problem Statement

India has 14 crore+ demat accounts, but most retail participants still operate with fragmented signals, delayed interpretation, and limited portfolio intelligence.

The objective is not to summarize data. The objective is to identify money-making opportunities earlier, explain why they matter, and provide auditable evidence.

## What MarketNerve Builds

1. Opportunity Radar
- Detects filing, flow, and anomaly opportunities and ranks by actionable score.

2. Chart Pattern Intelligence
- Scans technical setups, explains context in plain English, and reports historical success rates.

3. Market ChatGPT Next Gen
- Provides source-cited, portfolio-aware responses with confidence and evidence highlights.

4. AI Market Video Engine
- Produces a daily market wrap plan with script outline, scene plan, render status, and output targets.

## Product Modules

- Signal Scout
- Pattern Mind
- Portfolio Lens
- Story Engine
- IPO Intelligence
- Audit Trail

## Tech Stack

- Frontend: Next.js App Router, React, Framer Motion
- Backend: FastAPI, Pydantic, async services
- Data: NSE and BSE fetchers, yfinance, Redis cache, PostgreSQL persistence
- AI: Mistral primary, Gemini fallback, structured JSON generation

## Monorepo Structure

- apps/web: user-facing web experience
- backend: intelligence APIs, data pipelines, scoring logic
- config/marketnerve.seed.json: deterministic fallback and bootstrap dataset
- docs: architecture and product documentation

## Quick Start

1. Install dependencies

```bash
cd apps/web
npm install
```

```bash
cd ../backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2. Start backend

```bash
cd backend
python -m uvicorn app.main:app --reload
```

3. Start frontend from repo root

```bash
npm run dev:web
```

Frontend runs on http://localhost:3000 and calls backend on http://localhost:8000 by default.

## Key Endpoints

- GET /api/signals
- GET /api/signals/performance
- GET /api/signals/calibration
- GET /api/patterns/scan
- GET /api/story/arcs
- GET /api/story/video/latest
- POST /api/story/video/generate
- POST /api/chat
- POST /api/portfolio/analyze
- POST /api/portfolio/query
- GET /api/health

## Build and Test

```bash
cd apps/web
npm run build
npm test
```

```bash
cd backend
pytest
```

## Demo Checklist

Before presenting:

1. Start backend and verify GET /api/health returns healthy.
2. Start frontend via npm run dev:web.
3. Verify Home, Signals, Chat, Portfolio, Story all load.
4. Trigger video generation and show queued to rendering to ready flow.
5. Open audit trails from Opportunity Radar evidence links.

## Documentation

- Detailed blueprint: docs/PRODUCT_BLUEPRINT.md
- Architecture notes: docs/ARCHITECTURE.md
- PlantUML diagram source: docs/arch.puml
- Architecture image placeholder: docs/arch.png

