"""
Patterns service — reads from repository, adds enrichment/filtering.
"""
from app.data.repository import repository


def _enrich_pattern(p: dict, idx: int) -> dict:
    pat = dict(p)
    # Normalise backtest fields (seed JSON uses different shape)
    if "backtest" in pat and isinstance(pat["backtest"], dict):
        bt = pat["backtest"]
        pat.setdefault("wins", bt.get("wins", 3))
        pat.setdefault("occurrences", bt.get("occurrences", 5))
        pat.setdefault("avg_30d_return", bt.get("avg_30d_return", 0.05))
        pat.setdefault("reward_risk_ratio", bt.get("reward_risk_ratio", 2.0))
    pat.setdefault("wins", 3)
    pat.setdefault("occurrences", 5)
    pat.setdefault("avg_30d_return", 0.05)
    pat.setdefault("reward_risk_ratio", 2.0)
    pat.setdefault("risk_flags", [])
    pat.setdefault("signal_strength", "Actionable")
    pat.setdefault("market_cap_band", "Large Cap")
    return pat


async def list_patterns(
    pattern_type: str = "",
    ticker: str = "",
    min_confidence: float = 0.0,
    limit: int = 20,
) -> list[dict]:
    raw = await repository.get_patterns()
    patterns = [_enrich_pattern(p, i) for i, p in enumerate(raw)]
    if pattern_type:
        patterns = [p for p in patterns if pattern_type.lower() in p.get("pattern_type", "").lower()]
    if ticker:
        patterns = [p for p in patterns if p.get("ticker", "").upper() == ticker.upper()]
    if min_confidence:
        patterns = [p for p in patterns if p.get("confidence", 0) >= min_confidence]
    patterns.sort(key=lambda p: p.get("confidence", 0), reverse=True)
    return patterns[:limit]


async def get_pattern_by_id(pattern_id: str) -> dict | None:
    raw = await repository.get_patterns()
    for p in raw:
        if p.get("id") == pattern_id:
            return _enrich_pattern(p, 0)
    return None


async def list_patterns_by_confidence(threshold: float = 0.78, limit: int = 10) -> list[dict]:
    return await list_patterns(min_confidence=threshold, limit=limit)


async def get_patterns_for_ticker(ticker: str) -> list[dict]:
    return await list_patterns(ticker=ticker, limit=10)
