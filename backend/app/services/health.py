from __future__ import annotations

from app.data.repository import repository
from app.models.schemas import HealthResponse


def get_health() -> HealthResponse:
    raw = repository.get_health()
    return HealthResponse(
        status=raw["status"],
        generated_at=repository.generated_at(),
        data_freshness_minutes=raw["data_freshness_minutes"],
        api_p95_ms=raw["api_p95_ms"],
        agent_status=raw["agent_status"],
        pipeline_status={
            "exchange_feed": "seeded-demo-mode",
            "filing_parser": "ready",
            "portfolio_analytics": "ready",
            "story_pipeline": "ready",
            "ipo_tracker": "ready",
            "websocket_broadcaster": "ready",
        },
        websocket_channels=[
            "ws://market-nerve.io/live/signals",
            "ws://market-nerve.io/live/patterns",
            "ws://market-nerve.io/live/filings",
        ],
        total_signals_processed=raw.get("total_signals_processed", 0),
        uptime_minutes=raw.get("uptime_minutes", 0),
    )
