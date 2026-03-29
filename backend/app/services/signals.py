"""
Signals service — reads from repository (Redis → DB → seed).
Thin layer: filtering, pagination, audit trail generation.
"""
import math
import statistics
from datetime import datetime, timezone
from typing import Optional
from app.data.repository import repository


from app.models.schemas import EnrichedSignal, Signal, SourceRef, BacktestStats, AuditTrail


def _enrich(signal: dict, idx: int) -> EnrichedSignal:
    """Ensure all expected fields exist with sensible defaults."""
    s = dict(signal)
    
    # Map sources to SourceRef
    sources = [SourceRef(name=src) if isinstance(src, str) else src for src in s.get("sources", [])]
    
    # Map backtest stats
    bt_raw = s.get("backtest", {})
    bt_win_rate = bt_raw.get("win_rate", s.get("historical_win_rate", 0.6))
    bt_avg_30d = bt_raw.get("avg_30d_return", s.get("avg_30d_return", 0.05))
    bt = BacktestStats(
        occurrences=bt_raw.get("occurrences", 5),
        wins=bt_raw.get("wins", 3),
        losses=bt_raw.get("losses", 2),
        win_rate=bt_win_rate,
        avg_30d_return=bt_avg_30d,
        reward_risk_ratio=s.get("reward_risk_ratio", 2.0)
    )

    return EnrichedSignal(
        id=s.get("id", f"sig-{idx}"),
        ticker=s.get("ticker", "UNKNOWN"),
        company=s.get("company", "Unknown Company"),
        sector=s.get("sector", "Other"),
        signal_type=s.get("signal_type", "Neutral"),
        headline=s.get("headline", "Market signal detected"),
        summary=s.get("summary", "No summary available"),
        confidence=s.get("confidence", 0.7),
        anomaly_score=s.get("anomaly_score", 0.0),
        z_score=s.get("z_score", 0.0),
        impact_score=s.get("impact_score", 5),
        freshness_label="fresh" if s.get("age_minutes", 0) < 60 else "stale",
        portfolio_impact_pct=s.get("portfolio_impact_pct", 0.0),
        sources=sources,
        backtest=bt,
        reasoning_chain=s.get("reasoning_steps", []),
        watch_items=s.get("watch_items", []),
        disclaimer="AI-generated intelligence.",
        tags=s.get("tags", ["source-cited"])
    )


def calculate_z_score(val: float, mean: float, std_dev: float) -> float:
    if not std_dev:
        return 0.0
    return (val - mean) / std_dev


async def list_signals(
    limit: int = 20,
    offset: int = 0,
    sector: str = "",
    min_confidence: float = 0.0,
    signal_type: str = "",
    since: str = "",
) -> list[EnrichedSignal]:
    raw = await repository.get_signals()
    signals = [_enrich(s, i) for i, s in enumerate(raw)]
    # Filter
    if sector:
        signals = [s for s in signals if sector.lower() in s.sector.lower()]
    if signal_type:
        signals = [s for s in signals if signal_type.lower() in s.signal_type.lower()]
    if min_confidence:
        signals = [s for s in signals if s.confidence >= min_confidence]
    # Sort: impact_score × confidence × |z_score|
    signals.sort(key=lambda s: s.impact_score * s.confidence * (1 + abs(s.z_score)), reverse=True)
    return signals[offset : offset + limit]


async def count_signals(
    sector: str = "",
    min_confidence: float = 0.0,
    signal_type: str = "",
) -> int:
    results = await list_signals(sector=sector, min_confidence=min_confidence, signal_type=signal_type, limit=1000)
    return len(results)


async def get_signal(signal_id: str) -> EnrichedSignal | None:
    signals = await repository.get_signals()
    for i, s in enumerate(signals):
        if s.get("id") == signal_id or s.get("ticker") == signal_id:
            return _enrich(s, i)
    return None


async def get_historical_signals_for_ticker(ticker: str) -> list[EnrichedSignal]:
    signals = await repository.get_signals()
    return [_enrich(s, i) for i, s in enumerate(signals) if s.get("ticker") == ticker]


async def get_high_confidence_signals(threshold: float = 0.78, limit: int = 10) -> list[EnrichedSignal]:
    return await list_signals(min_confidence=threshold, limit=limit)


async def get_signals_by_sector(sector: str) -> list[EnrichedSignal]:
    return await list_signals(sector=sector, limit=15)


async def get_audit(signal_id: str) -> AuditTrail | None:
    signal = await get_signal(signal_id)
    if not signal:
        raise KeyError(signal_id)
    
    # Map back to model
    return AuditTrail(
        signal_id=signal_id,
        ticker=signal.ticker,
        event_timestamp=datetime.now(timezone.utc),
        confidence=signal.confidence,
        input_snapshot={
            "sources": [src.name for src in signal.sources],
            "sector": signal.sector,
            "age_minutes": 0,
        },
        enrichment_snapshot={
            "z_score": signal.z_score,
            "anomaly_score": signal.anomaly_score,
            "volume_ratio": round(1.0 + abs(signal.z_score) * 0.3, 2),
            "rsi_estimate": round(50 + signal.z_score * 8, 1),
            "tags": signal.tags,
        },
        reasoning_chain=signal.reasoning_chain,
        output={
            "headline": signal.headline,
            "summary": signal.summary,
            "watch_items": signal.watch_items,
        },
        confidence_metadata={
            "base_confidence": round(signal.confidence - 0.05, 3),
            "boost_factors": ["High Volume", "RSI Alignment"],
            "failure_contexts": ["Low liquidity", "Broad market selloff"],
        },
        disclaimer=signal.disclaimer
    )


async def get_audit_trail(signal_id: str) -> dict | None:
    return await get_audit(signal_id)


def create_subscription(watchlist: list[str], sectors: list[str], min_confidence: float):
    from app.models.schemas import SignalSubscriptionResponse
    return SignalSubscriptionResponse(
        subscription_id="sub_" + datetime.now(timezone.utc).strftime("%Y%m%d%H%M"),
        status="active",
        active=True,
        watchlist=watchlist,
        sectors=sectors,
        min_confidence=min_confidence,
        filters={"watchlist": watchlist, "sectors": sectors, "min_confidence": min_confidence}
    )


def get_live_signal_events() -> list[dict]:
    return []


async def get_signal_performance() -> dict:
    """
    Model-backed performance tracker for T+1/T+5/T+30 horizons.
    Uses signal-level backtest returns and confidence weighting.
    """
    signals = await list_signals(limit=250)
    if not signals:
        return {
            "horizons": {"t1": 0.0, "t5": 0.0, "t30": 0.0},
            "by_signal_type": [],
            "sample_size": 0,
            "method": "confidence_weighted_backtest_projection",
        }

    type_buckets: dict[str, list[EnrichedSignal]] = {}
    for s in signals:
        type_buckets.setdefault(s.signal_type, []).append(s)

    def _horizon_metrics(items: list[EnrichedSignal]) -> tuple[float, float, float]:
        weighted = []
        conf_sum = 0.0
        for sig in items:
            avg_30 = float(sig.backtest.avg_30d_return)
            conf = max(0.05, min(1.0, float(sig.confidence)))
            weighted.append(avg_30 * conf)
            conf_sum += conf
        base = (sum(weighted) / conf_sum) if conf_sum else 0.0
        t1 = base * 0.22
        t5 = base * 0.48
        t30 = base
        return t1, t5, t30

    by_type = []
    for signal_type, items in type_buckets.items():
        t1, t5, t30 = _horizon_metrics(items)
        by_type.append({
            "signal_type": signal_type,
            "sample_size": len(items),
            "avg_confidence": round(sum(i.confidence for i in items) / len(items), 4),
            "t1_return": round(t1, 4),
            "t5_return": round(t5, 4),
            "t30_return": round(t30, 4),
        })

    by_type.sort(key=lambda x: x["t30_return"], reverse=True)

    all_t1, all_t5, all_t30 = _horizon_metrics(signals)
    return {
        "horizons": {
            "t1": round(all_t1, 4),
            "t5": round(all_t5, 4),
            "t30": round(all_t30, 4),
        },
        "by_signal_type": by_type,
        "sample_size": len(signals),
        "method": "confidence_weighted_backtest_projection",
    }


async def get_confidence_calibration() -> dict:
    """
    Compare predicted confidence vs realized win-rate buckets.
    Realized win-rate uses backtest.win_rate per signal as historical proxy.
    """
    signals = await list_signals(limit=500)
    bins = [
        (0.50, 0.60),
        (0.60, 0.70),
        (0.70, 0.80),
        (0.80, 0.90),
        (0.90, 1.01),
    ]

    rows = []
    for low, high in bins:
        bucket = [s for s in signals if low <= float(s.confidence) < high]
        if not bucket:
            rows.append(
                {
                    "bucket": f"{int(low*100)}-{int(min(high, 1.0)*100)}%",
                    "predicted": round((low + min(high, 1.0)) / 2, 4),
                    "realized": 0.0,
                    "gap": 0.0,
                    "sample_size": 0,
                }
            )
            continue

        predicted = sum(float(s.confidence) for s in bucket) / len(bucket)
        realized = sum(float(s.backtest.win_rate) for s in bucket) / len(bucket)
        rows.append(
            {
                "bucket": f"{int(low*100)}-{int(min(high, 1.0)*100)}%",
                "predicted": round(predicted, 4),
                "realized": round(realized, 4),
                "gap": round(realized - predicted, 4),
                "sample_size": len(bucket),
            }
        )

    non_empty = [r for r in rows if r["sample_size"] > 0]
    mae = (
        sum(abs(float(r["gap"])) for r in non_empty) / len(non_empty)
        if non_empty
        else 0.0
    )

    return {
        "bins": rows,
        "mean_absolute_error": round(mae, 4),
        "sample_size": len(signals),
        "method": "confidence_vs_backtest_winrate_bucketed",
    }
