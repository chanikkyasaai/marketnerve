from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.models.schemas import SignalSubscriptionRequest
from app.services.signals import (
    count_signals,
    create_subscription,
    get_audit,
    get_confidence_calibration,
    get_high_confidence_signals,
    get_signal_performance,
    get_historical_signals_for_ticker,
    get_signal,
    get_signals_by_sector,
    list_signals,
)


router = APIRouter(prefix="/signals", tags=["signals"])


@router.get("")
async def signals(
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
    sector: str | None = None,
    signal_type: str | None = None,
    min_confidence: float = Query(0.0, ge=0.0, le=1.0),
    since: str | None = None,
) -> dict:
    items = await list_signals(limit, offset, sector, min_confidence, signal_type, since)
    total = await count_signals(sector, min_confidence, signal_type)
    serialized_items = [s.model_dump() for s in items] if items and hasattr(items[0], "model_dump") else items
    return {
        "items": serialized_items,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": (offset + limit) < total,
    }


@router.get("/latest")
async def signals_latest(
    limit: int = Query(5, ge=1, le=20),
    threshold: float = Query(0.75, ge=0.0, le=1.0),
) -> dict:
    items = await get_high_confidence_signals(threshold=threshold, limit=limit)
    serialized_items = [s.model_dump() for s in items] if items and hasattr(items[0], "model_dump") else items
    return {"items": serialized_items, "threshold": threshold}


@router.get("/performance")
async def signals_performance() -> dict:
    return await get_signal_performance()


@router.get("/calibration")
async def signals_calibration() -> dict:
    return await get_confidence_calibration()


@router.get("/sector/{sector}")
async def signals_by_sector(sector: str) -> dict:
    items = await get_signals_by_sector(sector)
    serialized_items = [s.model_dump() for s in items] if items and hasattr(items[0], "model_dump") else items
    return {"items": serialized_items, "sector": sector}


@router.get("/audit/{signal_id}")
async def audit(signal_id: str) -> dict:
    try:
        trail = await get_audit(signal_id)
        return trail.model_dump(mode="json") if hasattr(trail, "model_dump") else trail
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Audit not found") from exc


# Note: wildcard must come AFTER more specific paths
@router.get("/{ticker_or_id}")
async def signal_detail(ticker_or_id: str) -> dict:
    try:
        signal = await get_signal(ticker_or_id)
        if not signal:
             raise HTTPException(status_code=404, detail="Signal not found")
        history = await get_historical_signals_for_ticker(signal["ticker"] if isinstance(signal, dict) else signal.ticker)
        serialized_history = [s.model_dump() for s in history] if history and hasattr(history[0], "model_dump") else history
        return {
            "signal": signal.model_dump() if hasattr(signal, "model_dump") else signal,
            "historical_signals": serialized_history,
        }
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Signal not found") from exc


@router.post("/subscribe")
def signal_subscribe(payload: SignalSubscriptionRequest) -> dict:
    return create_subscription(payload.watchlist, payload.sectors, payload.min_confidence).model_dump()
