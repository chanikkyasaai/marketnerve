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
async def pattern_scan(
    pattern_type: str | None = None,
    ticker: str | None = None,
    sector: str | None = None,
    market_cap_band: str | None = None,
    min_confidence: float = Query(0.0, ge=0.0, le=1.0),
) -> dict:
    patterns = await list_patterns(pattern_type, ticker, min_confidence)
    return {"items": [p.model_dump() if hasattr(p, "model_dump") else p for p in patterns], "count": len(patterns)}


@router.get("/high-conviction")
async def high_conviction_patterns(min_confidence: float = Query(0.75, ge=0.0, le=1.0)) -> dict:
    patterns = await list_patterns_by_confidence(threshold=min_confidence)
    return {"items": [p.model_dump() if hasattr(p, "model_dump") else p for p in patterns], "min_confidence": min_confidence}


@router.get("/id/{pattern_id}")
async def pattern_by_id(pattern_id: str) -> dict:
    try:
        p = await get_pattern_by_id(pattern_id)
        if not p:
             raise HTTPException(status_code=404, detail="Pattern not found")
        return p.model_dump() if hasattr(p, "model_dump") else p
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Pattern not found") from exc


@router.get("/{ticker}")
async def pattern_detail(ticker: str) -> dict:
    patterns = await get_ticker_patterns(ticker)
    if not patterns:
        raise HTTPException(status_code=404, detail=f"No patterns found for ticker: {ticker}")
    return {"ticker": ticker.upper(), "items": [p.model_dump() if hasattr(p, "model_dump") else p for p in patterns]}
