"""
Full Signal Pipeline:
1. Fetch OHLCV snapshots from yfinance for 25 NSE stocks
2. Detect anomalies (volume z-score > 1.8, RSI extremes, momentum)
3. Fetch NSE corporate announcements
4. For each anomaly → Gemini generates narrative signal
5. Store in Neon DB + Upstash Redis cache
"""
import asyncio
import logging
import uuid
from datetime import datetime, timezone

from app.data.yfinance_fetcher import fetch_all_snapshots, WATCHLIST
from app.data.nse_fetcher import fetch_corporate_announcements, fetch_fii_dii, format_announcements_for_gemini
from app.ai.gemini_client import generate_signal
from app.cache.redis_client import cache_set
from app.core.config import settings

logger = logging.getLogger(__name__)

SIGNAL_THRESHOLD_Z = 1.8       # Volume z-score to trigger signal
SIGNAL_THRESHOLD_DAY_PCT = 2.5 # Intraday % move to trigger signal
SIGNAL_THRESHOLD_RSI_LOW = 34  # RSI lower bound
SIGNAL_THRESHOLD_RSI_HIGH = 68 # RSI upper bound
MAX_SIGNALS_PER_RUN = 12       # Respects Gemini 15 RPM limit

# Fallback signal generator (no Gemini)
def _build_fallback_signal(snap: dict, reason: str) -> dict:
    ticker = snap["ticker"]
    z = snap.get("z_score", 0)
    conf = min(0.92, 0.60 + abs(z) * 0.08)
    return {
        "id": f"sig_{ticker}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M')}",
        "ticker": ticker,
        "company": snap["company"],
        "sector": snap["sector"],
        "signal_type": "Volume Anomaly" if abs(z) > 2 else "Momentum Surge",
        "headline": f"{snap['company']} — {reason}",
        "summary": (
            f"{snap['company']} ({ticker}) shows {reason.lower()} with volume at "
            f"{snap.get('volume_ratio', 1):.1f}× 20-day average. "
            f"RSI at {snap.get('rsi_14', 50):.0f}, day change {snap.get('day_change_pct', 0):+.2f}%."
        ),
        "confidence": round(conf, 2),
        "anomaly_score": round(abs(z), 2),
        "z_score": round(z, 2),
        "reward_risk_ratio": round(2.0 + abs(z) * 0.3, 1),
        "portfolio_impact_pct": round(abs(snap.get("day_change_pct", 0)) * 0.6, 1),
        "impact_score": min(10, int(abs(z) * 2.5 + 3)),
        "age_minutes": 0,
        "sources": ["NSE Live Feed", "yfinance", "Volume Analysis"],
        "reasoning_steps": [
            f"Volume z-score of {z:.1f}σ indicates institutional activity above normal.",
            f"RSI at {snap.get('rsi_14', 50):.0f} — {'oversold region' if snap.get('rsi_14', 50) < 40 else 'momentum building'}.",
            f"Price {'above' if snap.get('above_sma_50') else 'below'} 50-day SMA.",
        ],
        "watch_items": [
            f"Monitor volume in next 2 trading sessions",
            f"Key level: ₹{snap.get('current_price', 0) * 1.05:.0f} (5% up)",
            f"Stop loss: ₹{snap.get('current_price', 0) * 0.95:.0f} (5% down)",
        ],
        "tags": ["live", "screened"],
        "historical_win_rate": 0.62,
        "avg_30d_return": 0.055,
    }


async def _is_anomaly(snap: dict) -> tuple[bool, str]:
    """Check if a stock snapshot qualifies as a signal."""
    z = snap.get("z_score", 0)
    rsi = snap.get("rsi_14", 50)
    day_pct = abs(snap.get("day_change_pct", 0))
    vol_ratio = snap.get("volume_ratio", 1)

    if abs(z) >= SIGNAL_THRESHOLD_Z:
        return True, f"Volume surge {vol_ratio:.1f}× average (z={z:.1f}σ)"
    if rsi < SIGNAL_THRESHOLD_RSI_LOW:
        return True, f"RSI oversold at {rsi:.0f} — potential reversal"
    if rsi > SIGNAL_THRESHOLD_RSI_HIGH:
        return True, f"RSI overbought at {rsi:.0f} — momentum check"
    if day_pct >= SIGNAL_THRESHOLD_DAY_PCT:
        return True, f"Intraday move of {snap.get('day_change_pct',0):+.2f}%"
    return False, ""


async def run_signal_pipeline(pool=None) -> list[dict]:
    """
    Full signal pipeline. Returns list of signal dicts.
    Saves to DB (if pool provided) + Redis cache.
    """
    logger.info("🔄 Signal pipeline starting…")
    signals: list[dict] = []

    # 1. Fetch market snapshots
    snapshots = await fetch_all_snapshots()
    if not snapshots:
        logger.warning("No snapshots fetched — yfinance may be rate-limited")
        return []

    # 2. Fetch NSE announcements and FII/DII (in parallel)
    announcements, fii_dii = await asyncio.gather(
        fetch_corporate_announcements(),
        fetch_fii_dii(),
        return_exceptions=True,
    )
    if isinstance(announcements, Exception):
        announcements = []
    if isinstance(fii_dii, Exception):
        fii_dii = {}

    # 3. Filter anomalies and score them
    candidates = []
    for snap in snapshots:
        is_sig, reason = await _is_anomaly(snap)
        if is_sig:
            candidates.append((snap, reason))

    # Sort by abs z-score (highest anomaly first)
    candidates.sort(key=lambda x: abs(x[0].get("z_score", 0)), reverse=True)
    candidates = candidates[:MAX_SIGNALS_PER_RUN]

    logger.info(f"Found {len(candidates)} signal candidates from {len(snapshots)} stocks")

    # 4. Gemini enrichment (rate-limited: 1 call/sec to stay under 15 RPM)
    for snap, reason in candidates:
        ticker = snap["ticker"]
        announcement_text = format_announcements_for_gemini(
            announcements if isinstance(announcements, list) else [],
            ticker
        )

        if settings.has_gemini:
            try:
                gemini_out = await generate_signal(snap, announcement_text)
                await asyncio.sleep(1.1)  # Respect 15 RPM limit
            except Exception as e:
                logger.error(f"Gemini failed for {ticker}: {e}")
                gemini_out = None
        else:
            gemini_out = None

        if gemini_out and isinstance(gemini_out, dict) and "headline" in gemini_out:
            signal = {
                "id": f"sig_{ticker}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M')}",
                "ticker": ticker,
                "company": snap["company"],
                "sector": snap["sector"],
                "age_minutes": 0,
                "impact_score": min(10, int(gemini_out.get("confidence", 0.7) * 10)),
                "historical_win_rate": 0.64,
                "avg_30d_return": 0.062,
                "sources": ["NSE Feed", "yfinance", "Gemini AI"],
                **gemini_out,
            }
        else:
            signal = _build_fallback_signal(snap, reason)

        signals.append(signal)

        # 5. Save to DB
        if pool:
            await _save_signal_to_db(pool, signal)

    # 6. Cache in Redis
    if signals:
        signal_dicts = [_serialize_signal(s) for s in signals]
        await cache_set("signals:all", signal_dicts, settings.signal_cache_ttl_seconds)
        logger.info(f"✅ Signal pipeline done: {len(signals)} signals cached")

    return signals


def _serialize_signal(s: dict) -> dict:
    """Convert signal to JSON-serializable dict."""
    return {
        "id": s.get("id", ""),
        "ticker": s.get("ticker", ""),
        "company": s.get("company", ""),
        "sector": s.get("sector", ""),
        "signal_type": s.get("signal_type", "Volume Anomaly"),
        "headline": s.get("headline", ""),
        "summary": s.get("summary", ""),
        "confidence": float(s.get("confidence", 0.7)),
        "anomaly_score": float(s.get("anomaly_score", 0)),
        "z_score": float(s.get("z_score", 0)),
        "impact_score": int(s.get("impact_score", 5)),
        "reward_risk_ratio": float(s.get("reward_risk_ratio", 2.0)),
        "portfolio_impact_pct": float(s.get("portfolio_impact_pct", 0)),
        "age_minutes": int(s.get("age_minutes", 0)),
        "sources": list(s.get("sources", [])),
        "reasoning_steps": list(s.get("reasoning_steps", [])),
        "watch_items": list(s.get("watch_items", [])),
        "tags": list(s.get("tags", [])),
        "historical_win_rate": float(s.get("historical_win_rate", 0.6)),
        "avg_30d_return": float(s.get("avg_30d_return", 0.05)),
    }


async def _save_signal_to_db(pool, signal: dict) -> None:
    try:
        async with pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO signals (
                    id, ticker, company, sector, signal_type, headline, summary,
                    confidence, anomaly_score, z_score, impact_score, reward_risk_ratio,
                    portfolio_impact_pct, age_minutes, sources, reasoning_steps,
                    watch_items, tags, historical_win_rate, avg_30d_return, updated_at
                ) VALUES (
                    $1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,
                    $15::jsonb,$16::jsonb,$17::jsonb,$18::jsonb,$19,$20,NOW()
                )
                ON CONFLICT (id) DO UPDATE SET
                    headline=EXCLUDED.headline,
                    summary=EXCLUDED.summary,
                    confidence=EXCLUDED.confidence,
                    updated_at=NOW()
            """,
            signal["id"], signal["ticker"], signal["company"], signal["sector"],
            signal.get("signal_type","Volume Anomaly"), signal["headline"], signal["summary"],
            signal["confidence"], signal.get("anomaly_score",0), signal.get("z_score",0),
            signal.get("impact_score",5), signal.get("reward_risk_ratio",2.0),
            signal.get("portfolio_impact_pct",0), 0,
            str(signal.get("sources",[])).replace("'",'"'),
            str(signal.get("reasoning_steps",[])).replace("'",'"'),
            str(signal.get("watch_items",[])).replace("'",'"'),
            str(signal.get("tags",[])).replace("'",'"'),
            signal.get("historical_win_rate",0.6), signal.get("avg_30d_return",0.05))
    except Exception as e:
        logger.error(f"Failed to save signal {signal.get('id')} to DB: {e}")
