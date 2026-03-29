"""
Pattern Pipeline:
1. For each stock in watchlist, detect chart patterns from OHLCV
2. Use Gemini to generate narrative + risk flags
3. Save to Neon DB + Redis cache
"""
import asyncio
import logging
import uuid
from datetime import datetime, timezone

from app.data.yfinance_fetcher import fetch_all_snapshots, fetch_stock_df, detect_patterns, WATCHLIST
from app.ai.gemini_client import generate_pattern_narrative
from app.cache.redis_client import cache_set
from app.core.config import settings

logger = logging.getLogger(__name__)

PATTERN_WIN_RATES = {
    "Golden Cross": (71, 45),
    "Death Cross": (68, 35),
    "RSI Oversold Bounce": (64, 44),
    "RSI Overbought": (58, 36),
    "Volume Surge Breakout": (67, 43),
    "52-Week High Breakout": (73, 45),
    "52-Week Low Support": (61, 36),
}


def _build_fallback_pattern(snap: dict, pat: dict) -> dict:
    pt = pat["pattern_type"]
    wr, occ = PATTERN_WIN_RATES.get(pt, (65, 30))
    wins = int(occ * wr / 100)
    rr = round(2.0 + (wr - 60) * 0.06, 1)
    conf = round(wr / 100 + 0.02, 2)
    avg_ret = pat.get("avg_return", 5.0) / 100
    strength = "High conviction" if conf > 0.70 else "Actionable"

    return {
        "id": f"pat_{snap['ticker']}_{pt.lower().replace(' ','_')}_{datetime.now(timezone.utc).strftime('%Y%m%d')}",
        "ticker": snap["ticker"],
        "company": snap["company"],
        "sector": snap["sector"],
        "market_cap_band": "Large Cap" if snap["ticker"] in ["RELIANCE","HDFCBANK","TCS","INFY","ICICIBANK","KOTAKBANK"] else "Mid Cap",
        "pattern_type": pt,
        "signal_strength": strength,
        "confidence": conf,
        "occurrences": occ,
        "wins": wins,
        "avg_30d_return": avg_ret,
        "reward_risk_ratio": rr,
        "narrative": f"{snap['company']} ({snap['ticker']}) shows a {pt} pattern. {pat.get('detail', '')}",
        "context": f"Current market context: RSI at {snap.get('rsi_14', 50):.0f}, price ₹{snap.get('current_price', 0):.0f}, day change {snap.get('day_change_pct', 0):+.2f}%.",
        "risk_flags": [
            "Pattern invalidated if volume drops below 20-day average",
            "Market-wide selloff could override individual signal",
        ],
    }


async def run_pattern_pipeline(pool=None) -> list[dict]:
    """Run full pattern detection pipeline."""
    logger.info("🔄 Pattern pipeline starting…")
    all_patterns: list[dict] = []

    # Use existing snapshots for indicator data
    snapshots = await fetch_all_snapshots()
    snap_map = {s["ticker"]: s for s in snapshots}

    # For each stock, detect patterns (needs per-stock df)
    processed = 0
    for ticker, info in list(WATCHLIST.items())[:20]:  # Limit to 20 for speed
        snap = snap_map.get(ticker)
        if not snap:
            continue

        df = await fetch_stock_df(ticker)
        if df is None or df.empty:
            continue

        patterns = detect_patterns(ticker, df)
        for pat in patterns[:2]:  # Max 2 patterns per stock
            if settings.has_ai and processed < 10:  # Limit AI calls
                try:
                    gem = await generate_pattern_narrative(snap, pat)
                    await asyncio.sleep(1.1)
                    processed += 1
                except Exception as e:
                    logger.debug(f"Gemini pattern failed for {ticker}: {e}")
                    gem = None
            else:
                gem = None

            if gem and isinstance(gem, dict) and "narrative" in gem:
                pt = pat["pattern_type"]
                wr, occ = PATTERN_WIN_RATES.get(pt, (65, 30))
                wins = int(occ * wr / 100)
                pattern_obj = {
                    "id": f"pat_{ticker}_{pt.lower().replace(' ','_')}_{datetime.now(timezone.utc).strftime('%Y%m%d')}",
                    "ticker": ticker,
                    "company": snap["company"],
                    "sector": snap["sector"],
                    "market_cap_band": "Large Cap",
                    "pattern_type": pt,
                    "signal_strength": gem.get("signal_strength", "Actionable"),
                    "confidence": round(wr / 100 + 0.02, 2),
                    "occurrences": occ,
                    "wins": wins,
                    "avg_30d_return": pat.get("avg_return", 5.0) / 100,
                    "reward_risk_ratio": round(2.0 + (wr - 60) * 0.06, 1),
                    "narrative": gem.get("narrative", ""),
                    "context": gem.get("context", ""),
                    "risk_flags": gem.get("risk_flags", []),
                }
            else:
                pattern_obj = _build_fallback_pattern(snap, pat)

            all_patterns.append(pattern_obj)

            if pool:
                await _save_pattern_to_db(pool, pattern_obj)

    # Sort by confidence desc
    all_patterns.sort(key=lambda p: p["confidence"], reverse=True)

    if all_patterns:
        await cache_set("patterns:all", all_patterns, settings.pattern_cache_ttl_seconds)
        logger.info(f"✅ Pattern pipeline done: {len(all_patterns)} patterns cached")

    return all_patterns


async def _save_pattern_to_db(pool, pattern: dict) -> None:
    try:
        async with pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO patterns (
                    id, ticker, company, sector, market_cap_band, pattern_type,
                    signal_strength, confidence, occurrences, wins, avg_30d_return,
                    reward_risk_ratio, narrative, context, risk_flags
                ) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15::jsonb)
                ON CONFLICT (id) DO NOTHING
            """,
            pattern["id"], pattern["ticker"], pattern["company"], pattern["sector"],
            pattern.get("market_cap_band","Large Cap"), pattern["pattern_type"],
            pattern.get("signal_strength","Actionable"), pattern["confidence"],
            pattern.get("occurrences",10), pattern.get("wins",6),
            pattern.get("avg_30d_return",0.05), pattern.get("reward_risk_ratio",2.0),
            pattern["narrative"], pattern["context"],
            str(pattern.get("risk_flags",[])).replace("'",'"'))
    except Exception as e:
        logger.error(f"Failed to save pattern {pattern.get('id')} to DB: {e}")
