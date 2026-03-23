from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.services.patterns import (
    get_pattern_by_id,
    get_ticker_patterns,
    list_patterns,
    list_patterns_by_confidence,
)


router = APIRouter(prefix="/patterns", tags=["patterns"])


@router.get("/scan")
def pattern_scan(
    pattern_type: str | None = None,
    ticker: str | None = None,
    sector: str | None = None,
    market_cap_band: str | None = None,
    min_confidence: float = Query(0.0, ge=0.0, le=1.0),
) -> dict:
    patterns = list_patterns(pattern_type, ticker, sector, market_cap_band, min_confidence)
    return {"items": [p.model_dump() for p in patterns], "count": len(patterns)}


@router.get("/high-conviction")
def high_conviction_patterns(min_confidence: float = Query(0.75, ge=0.0, le=1.0)) -> dict:
    patterns = list_patterns_by_confidence(min_conf=min_confidence)
    return {"items": [p.model_dump() for p in patterns], "min_confidence": min_confidence}


@router.get("/id/{pattern_id}")
def pattern_by_id(pattern_id: str) -> dict:
    try:
        return get_pattern_by_id(pattern_id).model_dump()
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Pattern not found") from exc


@router.get("/{ticker}")
def pattern_detail(ticker: str) -> dict:
    patterns = get_ticker_patterns(ticker)
    if not patterns:
        raise HTTPException(status_code=404, detail=f"No patterns found for ticker: {ticker}")
    return {"ticker": ticker.upper(), "items": [p.model_dump() for p in patterns]}
