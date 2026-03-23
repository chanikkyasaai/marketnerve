from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.health import router as health_router
from app.api.routes.ipo import router as ipo_router
from app.api.routes.patterns import router as patterns_router
from app.api.routes.portfolio import router as portfolio_router
from app.api.routes.signals import router as signals_router
from app.api.routes.story import router as story_router
from app.api.websockets.streams import router as streams_router
from app.core.config import get_cors_origins

logger = logging.getLogger("marketnerve")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s — %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("MarketNerve API starting up — seeded data mode active.")
    yield
    logger.info("MarketNerve API shutting down.")


app = FastAPI(
    title="MarketNerve API",
    version="1.0.0",
    description=(
        "Autonomous Indian equities intelligence platform. "
        "Four core agents: Signal Scout, Pattern Mind, Portfolio Lens, Story Engine."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api")
app.include_router(signals_router, prefix="/api")
app.include_router(patterns_router, prefix="/api")
app.include_router(portfolio_router, prefix="/api")
app.include_router(story_router, prefix="/api")
app.include_router(ipo_router, prefix="/api")
app.include_router(streams_router, prefix="/live")
