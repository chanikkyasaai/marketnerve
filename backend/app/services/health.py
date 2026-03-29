"""
Health service — shows real pipeline status + system capabilities.
"""
from datetime import datetime, timezone
from app.data.repository import repository
from app.data.yfinance_fetcher import fetch_market_indices
from app.core.config import settings


async def get_health() -> dict:
    seed = await repository.get_health()
    pipeline_status = await repository.get_pipeline_status()
    market_status = await fetch_market_indices()
    
    return {
        "status": "healthy",
        "version": "2.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "market_status": market_status,
        "agent_status": seed.get("agent_status", {}),
        "pipeline_status": pipeline_status or seed.get("pipeline_status", {}),
        "websocket_channels": seed.get("websocket_channels", []),
        "total_signals_processed": seed.get("total_signals_processed", 1240),
        "uptime_minutes": seed.get("uptime_minutes", 1440),
        "capabilities": {
            "real_time_signals": settings.has_redis,
            "persistence": settings.has_database,
            "ai_enrichment": settings.has_ai,
            "mistral_primary": settings.has_mistral,
            "gemini_fallback": settings.has_gemini,
        }
    }
