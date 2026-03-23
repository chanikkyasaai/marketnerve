# MarketNerve

MarketNerve is a full-stack prototype of an autonomous market-intelligence product for Indian equities. This repository implements the hackathon priority stack from the product document: Signal Scout, Pattern Mind, Portfolio Lens, Story Engine, IPO Intelligence, and the shared audit trail.

The current build is backend-aware rather than purely static:

- frontend pages fetch from the FastAPI intelligence layer when it is available
- resilient seed-data fallbacks keep the product demoable offline
- Portfolio Lens supports analysis and Q&A requests against demo data or pasted CSV text
- signals, patterns, and story views expose real filtering and search flows

## Monorepo layout

- `apps/web`: Next.js App Router frontend
- `backend`: FastAPI backend and domain services
- `config/marketnerve.seed.json`: shared demo dataset used by frontend and backend
- `docs`: architecture notes, build log, and environment guidance

## Local setup

### 1. Frontend

```bash
cd apps/web
npm install
npm run dev
```

### 2. Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The frontend expects the backend at `http://localhost:8000` by default. Override `NEXT_PUBLIC_API_BASE_URL` in `apps/web/.env.local` if needed.

## Testing

```bash
cd backend
pytest
```

```bash
cd apps/web
npm test
```

## Environment

Copy the root `.env.example`, `apps/web/.env.example`, and `backend/.env.example` into real env files when you are ready to plug in live providers.

No API keys are required for the seeded demo mode. Keys become relevant only when switching from seeded data to live LLM, auth, database, or queue integrations.
