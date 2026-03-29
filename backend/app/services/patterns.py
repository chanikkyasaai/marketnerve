"""
Patterns service — reads from repository, adds enrichment/filtering.
"""
from app.data.repository import repository
from app.models.schemas import Pattern


def _enrich_pattern(p: dict, idx: int) -> Pattern:
    pat = dict(p)
    # Normalise backtest fields
    bt = pat.get("backtest", {})
    wins = bt.get("wins", 3)
    occurrences = bt.get("occurrences", 5)
    avg_30d_return = bt.get("avg_30d_return", 0.05)
    reward_risk_ratio = bt.get("reward_risk_ratio", 2.0)

    return Pattern(
        id=pat.get("id", f"pat-{idx}"),
        ticker=pat.get("ticker", "UNKNOWN"),
        company=pat.get("company", "Unknown Company"),
        pattern_type=pat.get("pattern_type", "Neutral"),
        confidence=pat.get("confidence", 0.7),
        occurrences=pat.get("occurrences", occurrences),
        wins=pat.get("wins", wins),
        avg_30d_return=pat.get("avg_30d_return", avg_30d_return),
        reward_risk_ratio=pat.get("reward_risk_ratio", reward_risk_ratio),
        narrative=pat.get("narrative", "Pattern detected."),
        context=pat.get("context", "Market context unavailable."),
        risk_flags=pat.get("risk_flags", [])
    )


async def list_patterns(
    pattern_type: str = "",
    ticker: str = "",
    min_confidence: float = 0.0,
    limit: int = 20,
) -> list[Pattern]:
    raw = await repository.get_patterns()
    patterns = [_enrich_pattern(p, i) for i, p in enumerate(raw)]
    if pattern_type:
        patterns = [p for p in patterns if pattern_type.lower() in p.pattern_type.lower()]
    if ticker:
        patterns = [p for p in patterns if p.ticker.upper() == ticker.upper()]
    if min_confidence:
        patterns = [p for p in patterns if p.confidence >= min_confidence]
    patterns.sort(key=lambda p: p.confidence, reverse=True)
    return patterns[:limit]


async def get_pattern_by_id(pattern_id: str) -> Pattern | None:
    raw = await repository.get_patterns()
    for i, p in enumerate(raw):
        if p.get("id") == pattern_id:
            return _enrich_pattern(p, i)
    return None


async def list_patterns_by_confidence(threshold: float = 0.78, min_conf: float = 0.0, limit: int = 10) -> list[Pattern]:
    conf = min_conf or threshold
    return await list_patterns(min_confidence=conf, limit=limit)


async def get_patterns_for_ticker(ticker: str) -> list[Pattern]:
    return await list_patterns(ticker=ticker, limit=10)


async def get_ticker_patterns(ticker: str) -> list[Pattern]:
    return await list_patterns(ticker=ticker, limit=10)


def get_live_pattern_events() -> list[dict]:
    return []
