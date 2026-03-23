from __future__ import annotations

from app.data.repository import repository
from app.models.schemas import BacktestStats, LiveEvent, PatternInsight


_SECTOR_MAP = {
    "HDFCBANK": "Financial Services",
    "RELIANCE": "Energy",
    "TATAMOTORS": "Automobile",
    "ZOMATO": "Consumer Internet",
    "PERSISTENT": "Information Technology",
    "ITC": "Consumer Goods",
    "TATASTEEL": "Metals & Mining",
    "ICICIBANK": "Financial Services",
    "INFY": "Information Technology",
    "NIFTY_IT": "Information Technology",
}

_MARKET_CAP_MAP = {
    "HDFCBANK": "Large Cap",
    "RELIANCE": "Large Cap",
    "TATAMOTORS": "Large Cap",
    "ZOMATO": "Large Cap",
    "PERSISTENT": "Mid Cap",
    "ITC": "Large Cap",
    "TATASTEEL": "Large Cap",
    "ICICIBANK": "Large Cap",
    "INFY": "Large Cap",
    "NIFTY_IT": "Index",
}


def _signal_strength(confidence: float) -> str:
    if confidence >= 0.80:
        return "High conviction"
    if confidence >= 0.72:
        return "Actionable"
    return "Emerging"


def _risk_flags_from_seed(item: dict) -> list[str]:
    """Use risk_flags from seed data if available, otherwise derive."""
    if item.get("risk_flags"):
        return item["risk_flags"]
    flags = []
    if item["confidence"] < 0.72:
        flags.append("Lower statistical confidence than top-quartile setups")
    if item["avg_30d_return"] < 0.055:
        flags.append("Reward profile is moderate rather than explosive")
    return flags


def _to_pattern_insight(item: dict) -> PatternInsight:
    occurrences = item["occurrences"]
    wins = item["wins"]
    losses = max(0, occurrences - wins)
    win_rate = round(wins / occurrences, 4)
    reward_risk = item.get("reward_risk_ratio")
    if reward_risk is None:
        failure_prob = max(1 - win_rate, 0.01)
        reward_risk = round(item["avg_30d_return"] / failure_prob, 2) if item["avg_30d_return"] > 0 else 0.0
    return PatternInsight(
        id=item.get("id", ""),
        ticker=item["ticker"],
        company=item["company"],
        sector=_SECTOR_MAP.get(item["ticker"], "Diversified"),
        market_cap_band=_MARKET_CAP_MAP.get(item["ticker"], "Large Cap"),
        pattern_type=item["pattern_type"],
        confidence=item["confidence"],
        signal_strength=_signal_strength(item["confidence"]),
        backtest=BacktestStats(
            occurrences=occurrences,
            wins=wins,
            losses=losses,
            win_rate=win_rate,
            avg_30d_return=item["avg_30d_return"],
            avg_holding_days=30,
            failure_contexts=["Index weakness", "Volume confirmation failed"],
            reward_risk_ratio=reward_risk,
        ),
        narrative=item["narrative"],
        context=item["context"],
        risk_flags=_risk_flags_from_seed(item),
    )


def list_patterns(
    pattern_type: str | None = None,
    ticker: str | None = None,
    sector: str | None = None,
    market_cap_band: str | None = None,
    min_confidence: float = 0.0,
) -> list[PatternInsight]:
    patterns = [_to_pattern_insight(item) for item in repository.get_patterns()]
    if pattern_type:
        patterns = [p for p in patterns if pattern_type.lower() in p.pattern_type.lower()]
    if ticker:
        patterns = [p for p in patterns if p.ticker.lower() == ticker.lower()]
    if sector:
        patterns = [p for p in patterns if p.sector.lower() == sector.lower()]
    if market_cap_band:
        patterns = [p for p in patterns if p.market_cap_band.lower() == market_cap_band.lower()]
    patterns = [p for p in patterns if p.confidence >= min_confidence]
    return sorted(patterns, key=lambda p: (-p.confidence, p.ticker))


def get_ticker_patterns(ticker: str) -> list[PatternInsight]:
    return list_patterns(ticker=ticker)


def get_pattern_by_id(pattern_id: str) -> PatternInsight:
    for item in repository.get_patterns():
        if item.get("id") == pattern_id:
            return _to_pattern_insight(item)
    raise KeyError(pattern_id)


def list_patterns_by_confidence(min_conf: float = 0.75) -> list[PatternInsight]:
    return list_patterns(min_confidence=min_conf)


def get_live_pattern_events() -> list[LiveEvent]:
    return [
        LiveEvent(
            channel="patterns",
            event_type="pattern_detected",
            generated_at=repository.generated_at(),
            payload={
                "ticker": pattern.ticker,
                "pattern_type": pattern.pattern_type,
                "confidence": pattern.confidence,
                "signal_strength": pattern.signal_strength,
                "reward_risk_ratio": pattern.backtest.reward_risk_ratio,
            },
        )
        for pattern in list_patterns()
    ]
