"""
Repository — unified data access layer.
Priority: Redis cache → Neon DB → Seed JSON fallback.
"""
import json
import logging
from pathlib import Path
from functools import lru_cache

from app.cache.redis_client import cache_get
from app.core.config import settings

logger = logging.getLogger(__name__)

@lru_cache(maxsize=1)
def _load_seed() -> dict:
    path = settings.get_data_path()
    if path.exists():
        with open(path) as f:
            return json.load(f)
    logger.warning(f"Seed file not found at {path}")
    return {}

async def _get_from_db_signals(pool) -> list[dict] | None:
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT id, ticker, company, sector, signal_type, headline, summary,
                       confidence, anomaly_score, z_score, impact_score, reward_risk_ratio,
                       portfolio_impact_pct, age_minutes, sources, reasoning_steps,
                       watch_items, tags, historical_win_rate, avg_30d_return
                FROM signals
                ORDER BY updated_at DESC, confidence DESC
                LIMIT 30
            """)
            if not rows:
                return None
            return [
                {
                    **dict(r),
                    "sources": json.loads(r["sources"]) if isinstance(r["sources"], str) else (r["sources"] or []),
                    "reasoning_steps": json.loads(r["reasoning_steps"]) if isinstance(r["reasoning_steps"], str) else (r["reasoning_steps"] or []),
                    "watch_items": json.loads(r["watch_items"]) if isinstance(r["watch_items"], str) else (r["watch_items"] or []),
                    "tags": json.loads(r["tags"]) if isinstance(r["tags"], str) else (r["tags"] or []),
                }
                for r in rows
            ]
    except Exception as e:
        logger.error(f"DB signals query failed: {e}")
        return None

async def _get_from_db_patterns(pool) -> list[dict] | None:
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT id, ticker, company, sector, market_cap_band, pattern_type,
                       signal_strength, confidence, occurrences, wins, avg_30d_return,
                       reward_risk_ratio, narrative, context, risk_flags
                FROM patterns
                ORDER BY created_at DESC, confidence DESC
                LIMIT 30
            """)
            if not rows:
                return None
            return [
                {
                    **dict(r),
                    "risk_flags": json.loads(r["risk_flags"]) if isinstance(r["risk_flags"], str) else (r["risk_flags"] or []),
                }
                for r in rows
            ]
    except Exception as e:
        logger.error(f"DB patterns query failed: {e}")
        return None


class Repository:
    def __init__(self):
        self._pool = None

    def set_pool(self, pool):
        self._pool = pool

    async def get_signals(self) -> list[dict]:
        # 1. Redis
        cached = await cache_get("signals:all")
        if cached:
            logger.debug("Signals: Redis hit")
            return cached
        # 2. DB
        if self._pool:
            from_db = await _get_from_db_signals(self._pool)
            if from_db:
                logger.debug(f"Signals: DB hit ({len(from_db)} rows)")
                return from_db
        # 3. Seed
        logger.debug("Signals: using seed fallback")
        return _load_seed().get("signals", [])

    async def get_patterns(self) -> list[dict]:
        cached = await cache_get("patterns:all")
        if cached:
            return cached
        if self._pool:
            from_db = await _get_from_db_patterns(self._pool)
            if from_db:
                return from_db
        return _load_seed().get("patterns", [])

    def get_portfolio(self) -> dict:
        return _load_seed().get("portfolio", {})

    def get_stories(self) -> list[dict]:
        return _load_seed().get("stories", [])

    def get_ipos(self) -> list[dict]:
        return _load_seed().get("ipos", [])

    def get_health(self) -> dict:
        return _load_seed().get("health", {})

    async def get_pipeline_status(self) -> dict:
        if not self._pool:
            return {"last_run": "never", "signals_generated": 0}
        try:
            async with self._pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT status, signals_generated, patterns_generated, started_at
                    FROM pipeline_runs ORDER BY started_at DESC LIMIT 1
                """)
            if row:
                return dict(row)
        except Exception:
            pass
        return {"last_run": "never", "signals_generated": 0}


repository = Repository()
