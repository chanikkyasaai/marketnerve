# Development Setup & Contributing Guide

## Quick Start

### Prerequisites
- Python 3.10+ (backend)
- Node.js 18+ (frontend)
- PostgreSQL 14+ (database)
- Redis 6+ (caching)

### 1. Environment Setup

```bash
# Clone the repository
git clone <repository-url>
cd marketnerve

# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# Add API keys for: Mistral, Gemini, etc.
# Add database URLs: POSTGRES_URL, REDIS_URL
```

#### Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `MARKETNERVE_ENV` | Environment mode | `development` or `production` |
| `POSTGRES_URL` | Database connection | `postgresql://user:pass@localhost/marketnerve` |
| `REDIS_URL` | Cache connection | `redis://localhost:6379` |
| `MISTRAL_API_KEY` | Primary LLM provider | `sk-xxx` |
| `GEMINI_API_KEY` | Fallback LLM provider | `AIzaSyxxx` |
| `NEXT_PUBLIC_API_BASE_URL` | Backend API URL (frontend) | `http://localhost:8000` |

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations (if applicable)
# python manage.py migrate

# Start development server
python -m uvicorn app.main:app --reload
# Runs on http://localhost:8000
```

### 3. Frontend Setup

```bash
cd apps/web

# Install dependencies
npm install
# or if using pnpm:
pnpm install

# Start development server
npm run dev
# or
pnpm dev
# Runs on http://localhost:3000
```

### 4. Verify Setup

```bash
# Backend health check
curl http://localhost:8000/health

# Frontend
Open http://localhost:3000 in browser
```

---

## Development Workflow

### Branch Strategy

```
main (production)
  └── staging (qa)
      └── develop (integration)
          ├── feature/signals-v2
          ├── feature/portfolio-optimization
          ├── bugfix/chart-rendering
          └── ...
```

### Creating a Feature Branch

```bash
git checkout develop
git pull origin develop
git checkout -b feature/your-feature-name

# Make changes
git add .
git commit -m "[module] description"
git push origin feature/your-feature-name

# Create Pull Request
```

### Code Style & Linting

#### Backend (Python)
```bash
cd backend

# Format code
black app tests

# Lint code
flake8 app tests
pylint app tests

# Type checking
pyright app

# Run tests
pytest tests/
pytest tests/test_signal_service.py -v  # Specific test
```

#### Frontend (JavaScript/React)
```bash
cd apps/web

# Format code
npm run format
# or
prettier --write .

# Lint code
npm run lint

# Run tests
npm test
```

---

## Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run specific test file
pytest tests/test_signal_service.py

# Run with coverage
pytest --cov=app tests/

# Run with verbose output
pytest -v --tb=short
```

### Frontend Tests

```bash
cd apps/web

# Run all tests
npm test

# Watch mode
npm test -- --watch

# Generate coverage report
npm test -- --coverage
```

### Integration Testing

```bash
# Start both servers
# Terminal 1: Backend
cd backend && python -m uvicorn app.main:app --reload

# Terminal 2: Frontend
cd apps/web && npm run dev

# Terminal 3: Run integration tests
npm run test:integration
```

---

## Building for Production

### Backend

```bash
cd backend

# Create production-ready build
# (No special build step needed; FastAPI is ready to serve)

# Can use Gunicorn for production
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app.main:app
```

### Frontend

```bash
cd apps/web

# Build Next.js application
npm run build

# Test production build locally
npm run start

# Build output is in .next/ directory
```

---

## Common Development Tasks

### Database Operations

```bash
# Backend database operations
cd backend

# Create new migration (if using Alembic/SQLAlchemy)
alembic revision --autogenerate -m "add new field"

# Apply migrations
alembic upgrade head

# Seed initial data
python app/data/seed.py
```

### API Testing

```bash
# Using curl
curl -X GET http://localhost:8000/signals

# Using httpie (if installed)
http GET localhost:8000/signals

# Using Postman or Insomnia: import the endpoints from /api/* routes

# Test with sample data
cd backend
python -c "
import asyncio
from app.pipeline.signal_pipeline import run_signal_pipeline
asyncio.run(run_signal_pipeline())
"
```

### Hot Reload & Debugging

#### Backend
```bash
# Debug mode (with verbose logging)
python -m uvicorn app.main:app --reload --log-level debug

# With debugger (add breakpoints in code)
python -m pdb -m uvicorn app.main:app --reload
```

#### Frontend
```bash
# Development mode (hot reload enabled by default)
npm run dev

# Debug in browser: F12 → Sources tab → Set breakpoints
```

---

## Troubleshooting

### Backend Issues

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Ensure venv is activated: `source .venv/bin/activate` |
| Database connection error | Check `POSTGRES_URL` in `.env` and pg is running |
| Redis connection error | Check `REDIS_URL` and Redis service is running |
| Port 8000 already in use | `lsof -i :8000` (macOS/Linux) or `netstat -ano \| findstr :8000` (Windows) |

### Frontend Issues

| Issue | Solution |
|-------|----------|
| `npm install` hangs | Try `npm cache clean --force` then `npm install` |
| Port 3000 in use | `npm run dev -- -p 3001` to use different port |
| API calls failing | Verify backend is running and `NEXT_PUBLIC_API_BASE_URL` is correct |
| Blank screens | Check browser console (F12) for errors |

### General

```bash
# Reset everything to clean state
git clean -fdx
git reset --hard HEAD

# Remove cache folders
rm -rf .next __pycache__ .pytest_cache .venv node_modules

# Reinstall from scratch
# (Follow setup steps again)
```

---

## Git Hygiene

### Before Every Commit

```bash
# Check for uncommitted changes
git status

# Verify .env files are NOT staged
git diff --cached | grep -E '\.env|password|api_key|secret'

# Verify nothing from node_modules or __pycache__ is staged
git diff --cached | grep -E 'node_modules|__pycache__'
```

### Commit Best Practices

```bash
# Good commit messages
git commit -m "[signals] add confidence calibration score calculation"
git commit -m "[portfolio] fix CSV parsing for special characters"
git commit -m "[docs] update architecture diagram with new pipeline"

# Bad commit messages
git commit -m "fixed stuff"
git commit -m "updates"
git commit -m "working version"
```

### Handling Accidental Commits

```bash
# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes)
git reset --hard HEAD~1

# Remove file from last commit
git reset HEAD~1 backend/.env
git commit --amend --no-edit
```

---

## Performance & Monitoring

### Backend Profiling

```bash
cd backend

# Profile a specific endpoint
python -m cProfile -s cumulative app.main:app

# Memory profiling
pip install memory-profiler
python -m memory_profiler app.main:py
```

### Frontend Performance

```bash
cd apps/web

# Analyze bundle size
npm run build
npm install -g serve
serve .next

# Lighthouse audit
npm run lighthouse
```

---

## Deployment Checklist

### Before Deploying to Production

- [ ] All tests passing: `pytest` and `npm test`
- [ ] Code linting passed: `black`, `flake8`, `prettier`
- [ ] `.env.production` configured with correct secrets
- [ ] Database migrations applied
- [ ] Redis configured
- [ ] Staging environment verified
- [ ] No untracked `.env` or sensitive files in repo
- [ ] Commit messages are clear
- [ ] PR reviewed and approved

### Environment Variables for Production

```env
MARKETNERVE_ENV=production
POSTGRES_URL=postgresql://prod-user:prod-pass@prod-db.cloud:5432/marketnerve
REDIS_URL=redis://prod-redis.cloud:6379
MISTRAL_API_KEY=<production-key>
GEMINI_API_KEY=<production-key>
NEXT_PUBLIC_API_BASE_URL=https://api.marketnerve.com
```

---

## Useful Commands Reference

```bash
# Quick start all services (requires shell scripting)
./scripts/dev.sh  # (if available)

# Kill processes on ports
# macOS/Linux:
lsof -ti:8000 | xargs kill -9  # Backend
lsof -ti:3000 | xargs kill -9  # Frontend

# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Check git status before commit
git status
git diff
git diff --staged

# View commit history
git log --oneline -10
git log --graph --all --decorate --oneline
```

---

## Need Help?

1. **Check existing issues**: `github.com/repo/issues`
2. **Read module documentation**: `docs/ARCHITECTURE.md`
3. **Check code comments**: Most functions are documented
4. **Ask in Discord/Slack**: Community chat

---

## Code Review Standards

### For Reviewers

- [ ] Code follows style guide (Prettier/Black)
- [ ] All tests pass
- [ ] No new `.env` or secrets are exposed
- [ ] Performance impact is acceptable
- [ ] Documentation is updated
- [ ] Commit messages are clear

### For Authors

- [ ] Code is formatted (`npm run format` / `black app`)
- [ ] Tests are included for new features
- [ ] Documentation/comments are clear
- [ ] No debug statements left in code
- [ ] Commit history is clean (squash if needed)

---

## Final Notes

- Always pull latest `develop` before starting new feature
- Keep commits small and focused
- Write descriptive commit messages
- Don't commit secrets or environment files
- Test locally before pushing
- Review CI/CD pipeline results

Happy coding! 🚀
