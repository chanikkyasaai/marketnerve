"""
MarketNerve FastAPI — main entrypoint.
Startup: DB migration → run pipeline → schedule 30-min refresh.
"""
import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.connection import run_migrations, get_pool, close_pool
from app.data.repository import repository

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

_pipeline_task: asyncio.Task | None = None


async def _run_pipeline_loop():
    """Background loop: run pipelines on startup and every N minutes."""
    from app.pipeline.signal_pipeline import run_signal_pipeline
    from app.pipeline.pattern_pipeline import run_pattern_pipeline

    pool = None
    if settings.has_database:
        pool = await get_pool()

    interval_secs = settings.pipeline_interval_minutes * 60

    while True:
        try:
            logger.info("🚀 Starting MarketNerve data pipeline…")
            signals = await run_signal_pipeline(pool)
            patterns = await run_pattern_pipeline(pool)
            logger.info(f"✅ Pipeline complete: {len(signals)} signals, {len(patterns)} patterns")

            # Log pipeline run
            if pool:
                async with pool.acquire() as conn:
                    await conn.execute("""
                        INSERT INTO pipeline_runs (run_type, status, signals_generated, patterns_generated, completed_at)
                        VALUES ('full', 'success', $1, $2, NOW())
                    """, len(signals), len(patterns))
        except Exception as e:
            logger.error(f"❌ Pipeline failed: {e}", exc_info=True)
            if pool:
                try:
                    async with pool.acquire() as conn:
                        await conn.execute("""
                            INSERT INTO pipeline_runs (run_type, status, error_message, completed_at)
                            VALUES ('full', 'error', $1, NOW())
                        """, str(e)[:500])
                except Exception:
                    pass

        logger.info(f"💤 Next pipeline run in {settings.pipeline_interval_minutes} minutes")
        await asyncio.sleep(interval_secs)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _pipeline_task
    logger.info("=" * 50)
    logger.info("  MarketNerve v2.0 — India Equities War Room")
    logger.info(f"  Gemini AI: {'✅' if settings.has_gemini else '❌'}")
    logger.info(f"  Neon DB:   {'✅' if settings.has_database else '❌'}")
    logger.info(f"  Redis:     {'✅' if settings.has_redis else '❌'}")
    logger.info("=" * 50)

    # Run DB migrations (non-fatal — falls back to seed data if DB unreachable)
    try:
        await run_migrations()
    except Exception as e:
        logger.warning(f"⚠️  DB migration skipped (offline mode): {e}")

    # Wire repository to DB pool (non-fatal)
    if settings.has_database:
        try:
            pool = await get_pool()
            repository.set_pool(pool)
        except Exception as e:
            logger.warning(f"⚠️  DB pool unavailable, using seed data: {e}")

    # Launch background pipeline as asyncio task
    _pipeline_task = asyncio.create_task(_run_pipeline_loop())

    yield

    # Shutdown
    if _pipeline_task and not _pipeline_task.done():
        _pipeline_task.cancel()
        try:
            await _pipeline_task
        except asyncio.CancelledError:
            pass
    await close_pool()
    logger.info("👋 MarketNerve shut down cleanly")


app = FastAPI(
    title="MarketNerve API",
    description="Autonomous market intelligence for Indian equities",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all routers
from app.api.routes import health, signals, patterns, portfolio, story, ipo, chat
app.include_router(health.router, prefix="/api")
app.include_router(signals.router, prefix="/api")
app.include_router(patterns.router, prefix="/api")
app.include_router(portfolio.router, prefix="/api")
app.include_router(story.router, prefix="/api")
app.include_router(ipo.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
