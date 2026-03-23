from __future__ import annotations

import math
from datetime import datetime, timedelta
from uuid import uuid4

from app.data.repository import repository
from app.models.schemas import (
    AuditTrail,
    BacktestStats,
    EnrichedSignal,
    LiveEvent,
    SignalSubscriptionResponse,
    SourceRef,
)


DISCLAIMER = "Historical pattern data, not a recommendation. MarketNerve is not SEBI-registered investment advice."

_SUBSCRIPTIONS: dict[str, dict] = {}

# Sentinel confidence level for high-confidence signals
HIGH_CONFIDENCE_THRESHOLD = 0.80


def _signal_timestamp(age_minutes: int) -> datetime:
    generated = datetime.fromisoformat(repository.generated_at())
    return generated - timedelta(minutes=age_minutes)


def _source_refs(raw_sources: list[str]) -> list[SourceRef]:
    return [SourceRef(name=source) for source in raw_sources]


def _signal_tags(item: dict) -> list[str]:
    tags = [item["sector"], item["signal_type"], "source-cited"]
    if item["confidence"] >= HIGH_CONFIDENCE_THRESHOLD:
        tags.append("high-confidence")
    if item.get("z_score", 0) >= 2.5:
        tags.append("high-anomaly")
    if item["portfolio_impact_pct"] > 0:
        tags.append("portfolio-relevant")
    if item["age_minutes"] <= 60:
        tags.append("fresh")
    return tags


def calculate_z_score(value: float, mean: float = 0.5, std_dev: float = 0.15) -> float:
    """Calculate Z-score for anomaly detection. Positive = above average."""
    if std_dev == 0:
        return 0.0
    return round((value - mean) / std_dev, 2)


def _derive_anomaly_score(item: dict) -> float:
    """Return existing anomaly_score from seed, or derive it from confidence."""
    raw = item.get("anomaly_score")
    if raw:
        return float(raw)
    return round(item["confidence"] * 4.2, 2)


def _derive_z_score(item: dict) -> float:
    """Return existing z_score from seed, or derive it."""
    raw = item.get("z_score")
    if raw:
        return float(raw)
    return calculate_z_score(item["confidence"])


def _to_enriched_signal(item: dict) -> EnrichedSignal:
    occurrences = max(3, round(item["historical_win_rate"] * 10))
    wins = max(1, round(item["historical_win_rate"] * occurrences))
    win_rate = round(wins / occurrences, 4)
    avg_return = item["avg_30d_return"]
    # Reward / risk ratio: avg_return per unit of failure probability
    failure_prob = max(1 - win_rate, 0.01)
    reward_risk = round(avg_return / failure_prob, 2) if avg_return > 0 else 0.0

    return EnrichedSignal(
        id=item["id"],
        ticker=item["ticker"],
        company=item["company"],
        sector=item["sector"],
        signal_type=item["signal_type"],
        headline=item["headline"],
        summary=item["summary"],
        confidence=item["confidence"],
        anomaly_score=_derive_anomaly_score(item),
        z_score=_derive_z_score(item),
        impact_score=item["impact_score"],
        freshness_label="fresh" if item["age_minutes"] <= 60 else "active",
        portfolio_impact_pct=item["portfolio_impact_pct"],
        sources=_source_refs(item["sources"]),
        backtest=BacktestStats(
            occurrences=occurrences,
            wins=wins,
            losses=max(0, occurrences - wins),
            win_rate=win_rate,
            avg_30d_return=avg_return,
            avg_holding_days=30,
            failure_contexts=[
                "Broad market corrections greater than 5%",
                "Sector-wide de-rating after earnings misses",
            ],
            reward_risk_ratio=reward_risk,
        ),
        reasoning_chain=item["reasoning_steps"],
        watch_items=item["watch_items"],
        disclaimer=DISCLAIMER,
        tags=_signal_tags(item),
    )


def list_signals(
    limit: int = 10,
    offset: int = 0,
    sector: str | None = None,
    min_confidence: float = 0.0,
    signal_type: str | None = None,
    since: str | None = None,
) -> list[EnrichedSignal]:
    signals = [_to_enriched_signal(item) for item in repository.get_signals()]
    if sector:
        signals = [s for s in signals if s.sector.lower() == sector.lower()]
    if signal_type:
        signals = [s for s in signals if s.signal_type.lower() == signal_type.lower()]
    signals = [s for s in signals if s.confidence >= min_confidence]
    if since:
        since_dt = datetime.fromisoformat(since)
        raw_map = {item["id"]: item for item in repository.get_signals()}
        signals = [
            s for s in signals
            if _signal_timestamp(raw_map[s.id]["age_minutes"]) >= since_dt
        ]
    ranked = sorted(signals, key=lambda s: (-s.impact_score, -s.confidence, s.ticker))
    return ranked[offset : offset + limit]


def count_signals(
    sector: str | None = None,
    min_confidence: float = 0.0,
    signal_type: str | None = None,
) -> int:
    signals = [_to_enriched_signal(item) for item in repository.get_signals()]
    if sector:
        signals = [s for s in signals if s.sector.lower() == sector.lower()]
    if signal_type:
        signals = [s for s in signals if s.signal_type.lower() == signal_type.lower()]
    return len([s for s in signals if s.confidence >= min_confidence])


def get_high_confidence_signals(threshold: float = HIGH_CONFIDENCE_THRESHOLD, limit: int = 5) -> list[EnrichedSignal]:
    """Return top signals above the confidence threshold, sorted by impact."""
    return list_signals(limit=limit, min_confidence=threshold)


def get_signal(signal_id: str) -> EnrichedSignal:
    for item in repository.get_signals():
        if item["id"] == signal_id or item["ticker"] == signal_id.upper():
            return _to_enriched_signal(item)
    raise KeyError(signal_id)


def get_historical_signals_for_ticker(ticker: str) -> list[EnrichedSignal]:
    return [s for s in list_signals(limit=100) if s.ticker.lower() == ticker.lower()]


def get_signals_by_sector(sector: str) -> list[EnrichedSignal]:
    return list_signals(limit=50, sector=sector)


def create_subscription(
    watchlist: list[str], sectors: list[str], min_confidence: float
) -> SignalSubscriptionResponse:
    subscription_id = f"sub-{uuid4().hex[:10]}"
    filters = {
        "watchlist": [ticker.upper() for ticker in watchlist],
        "sectors": sectors,
        "min_confidence": min_confidence,
    }
    _SUBSCRIPTIONS[subscription_id] = filters
    return SignalSubscriptionResponse(
        subscription_id=subscription_id,
        stream="ws://market-nerve.io/live/signals",
        filters=filters,
        active=True,
    )


def get_live_signal_events() -> list[LiveEvent]:
    events = []
    for signal in list_signals(limit=10):
        events.append(
            LiveEvent(
                channel="signals",
                event_type="signal_detected",
                generated_at=repository.generated_at(),
                payload={
                    "signal_id": signal.id,
                    "ticker": signal.ticker,
                    "headline": signal.headline,
                    "confidence": signal.confidence,
                    "anomaly_score": signal.anomaly_score,
                    "z_score": signal.z_score,
                    "portfolio_impact_pct": signal.portfolio_impact_pct,
                    "tags": signal.tags,
                },
            )
        )
    return events


def get_audit(signal_id: str) -> AuditTrail:
    signal = get_signal(signal_id)
    raw_map = {item["id"]: item for item in repository.get_signals()}
    raw = raw_map.get(signal.id, {})
    return AuditTrail(
        signal_id=signal.id,
        ticker=signal.ticker,
        event_timestamp=_signal_timestamp(raw.get("age_minutes", 0)),
        confidence=signal.confidence,
        input_snapshot={
            "sources": [s.name for s in signal.sources],
            "sector": signal.sector,
            "signal_type": signal.signal_type,
            "age_minutes": raw.get("age_minutes", 0),
        },
        enrichment_snapshot={
            "anomaly_score": signal.anomaly_score,
            "z_score": signal.z_score,
            "portfolio_impact_pct": signal.portfolio_impact_pct,
            "watch_items": signal.watch_items,
            "freshness_label": signal.freshness_label,
            "tags": signal.tags,
        },
        reasoning_chain=signal.reasoning_chain,
        output={
            "headline": signal.headline,
            "summary": signal.summary,
            "watch_items": signal.watch_items,
            "impact_score": signal.impact_score,
        },
        confidence_metadata={
            "backtest_win_rate": signal.backtest.win_rate,
            "occurrences": signal.backtest.occurrences,
            "avg_30d_return": signal.backtest.avg_30d_return,
            "reward_risk_ratio": signal.backtest.reward_risk_ratio,
            "failure_contexts": signal.backtest.failure_contexts,
        },
        disclaimer=signal.disclaimer,
    )
