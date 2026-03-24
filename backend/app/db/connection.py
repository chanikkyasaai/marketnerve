"""Neon PostgreSQL connection pool using asyncpg."""
import asyncpg
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

_pool: asyncpg.Pool | None = None

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS signals (
    id TEXT PRIMARY KEY,
    ticker TEXT NOT NULL,
    company TEXT NOT NULL,
    sector TEXT NOT NULL,
    signal_type TEXT NOT NULL,
    headline TEXT NOT NULL,
    summary TEXT NOT NULL,
    confidence FLOAT NOT NULL DEFAULT 0.7,
    anomaly_score FLOAT DEFAULT 0.0,
    z_score FLOAT DEFAULT 0.0,
    impact_score INT DEFAULT 5,
    age_minutes INT DEFAULT 0,
    portfolio_impact_pct FLOAT DEFAULT 0.0,
    sources JSONB DEFAULT '[]'::JSONB,
    reasoning_steps JSONB DEFAULT '[]'::JSONB,
    watch_items JSONB DEFAULT '[]'::JSONB,
    historical_win_rate FLOAT DEFAULT 0.6,
    avg_30d_return FLOAT DEFAULT 0.08,
    reward_risk_ratio FLOAT DEFAULT 2.0,
    tags JSONB DEFAULT '[]'::JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS patterns (
    id TEXT PRIMARY KEY,
    ticker TEXT NOT NULL,
    company TEXT NOT NULL,
    sector TEXT NOT NULL,
    market_cap_band TEXT DEFAULT 'Large Cap',
    pattern_type TEXT NOT NULL,
    signal_strength TEXT DEFAULT 'Actionable',
    confidence FLOAT NOT NULL DEFAULT 0.7,
    occurrences INT DEFAULT 5,
    wins INT DEFAULT 3,
    avg_30d_return FLOAT DEFAULT 0.08,
    reward_risk_ratio FLOAT DEFAULT 2.0,
    narrative TEXT NOT NULL,
    context TEXT NOT NULL,
    risk_flags JSONB DEFAULT '[]'::JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS market_snapshots (
    ticker TEXT PRIMARY KEY,
    company TEXT NOT NULL,
    sector TEXT DEFAULT 'Unknown',
    current_price FLOAT,
    prev_close FLOAT,
    day_change_pct FLOAT DEFAULT 0.0,
    volume BIGINT DEFAULT 0,
    avg_volume_20d BIGINT DEFAULT 0,
    volume_ratio FLOAT DEFAULT 1.0,
    rsi_14 FLOAT,
    macd_signal TEXT DEFAULT 'neutral',
    above_sma_50 BOOLEAN DEFAULT FALSE,
    above_sma_200 BOOLEAN DEFAULT FALSE,
    week_52_high FLOAT,
    week_52_low FLOAT,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS pipeline_runs (
    id SERIAL PRIMARY KEY,
    run_type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'running',
    signals_generated INT DEFAULT 0,
    patterns_generated INT DEFAULT 0,
    error_message TEXT,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_signals_ticker ON signals(ticker);
CREATE INDEX IF NOT EXISTS idx_signals_sector ON signals(sector);
CREATE INDEX IF NOT EXISTS idx_signals_updated ON signals(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_patterns_ticker ON patterns(ticker);
CREATE INDEX IF NOT EXISTS idx_patterns_updated ON patterns(created_at DESC);
"""

async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            dsn=settings.database_url,
            min_size=2,
            max_size=10,
            command_timeout=30,
        )
    return _pool

async def run_migrations() -> None:
    """Create tables if they don't exist."""
    if not settings.has_database:
        logger.warning("DATABASE_URL not set — skipping migration")
        return
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.execute(SCHEMA_SQL)
        logger.info("✅ Database migration complete")
    except Exception as e:
        logger.error(f"❌ Database migration failed: {e}")

async def close_pool() -> None:
    global _pool
    if _pool:
        await _pool.close()
        _pool = None
