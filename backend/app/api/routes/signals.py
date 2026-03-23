from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.models.schemas import SignalSubscriptionRequest
from app.services.signals import (
    count_signals,
    create_subscription,
    get_audit,
    get_high_confidence_signals,
    get_historical_signals_for_ticker,
    get_signal,
    get_signals_by_sector,
    list_signals,
)


router = APIRouter(prefix="/signals", tags=["signals"])


@router.get("")
def signals(
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
    sector: str | None = None,
    signal_type: str | None = None,
    min_confidence: float = Query(0.0, ge=0.0, le=1.0),
    since: str | None = None,
) -> dict:
    items = list_signals(limit, offset, sector, min_confidence, signal_type, since)
    total = count_signals(sector, min_confidence, signal_type)
    return {
        "items": [s.model_dump() for s in items],
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": (offset + limit) < total,
    }


@router.get("/latest")
def signals_latest(
    limit: int = Query(5, ge=1, le=20),
    threshold: float = Query(0.75, ge=0.0, le=1.0),
) -> dict:
    items = get_high_confidence_signals(threshold=threshold, limit=limit)
    return {"items": [s.model_dump() for s in items], "threshold": threshold}


@router.get("/sector/{sector}")
def signals_by_sector(sector: str) -> dict:
    return {"items": [s.model_dump() for s in get_signals_by_sector(sector)], "sector": sector}


@router.get("/audit/{signal_id}")
def audit(signal_id: str) -> dict:
    try:
        return get_audit(signal_id).model_dump(mode="json")
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Audit not found") from exc


# Note: wildcard must come AFTER more specific paths
@router.get("/{ticker_or_id}")
def signal_detail(ticker_or_id: str) -> dict:
    try:
        signal = get_signal(ticker_or_id)
        history = get_historical_signals_for_ticker(signal.ticker)
        return {
            "signal": signal.model_dump(),
            "historical_signals": [s.model_dump() for s in history],
        }
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Signal not found") from exc


@router.post("/subscribe")
def signal_subscribe(payload: SignalSubscriptionRequest) -> dict:
    return create_subscription(payload.watchlist, payload.sectors, payload.min_confidence).model_dump()
