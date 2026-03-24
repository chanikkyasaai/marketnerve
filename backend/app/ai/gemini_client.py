"""
Google Gemini 1.5 Flash — structured JSON output client.
Used for signal reasoning, portfolio Q&A, and pattern narratives.
"""
import asyncio
import json
import logging
from typing import Any

import google.generativeai as genai
from app.core.config import settings

logger = logging.getLogger(__name__)

_model = None

def _get_model():
    global _model
    if _model is None and settings.has_gemini:
        genai.configure(api_key=settings.gemini_api_key)
        _model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config={
                "response_mime_type": "application/json",
                "temperature": 0.4,
                "max_output_tokens": 1024,
            },
        )
    return _model


async def gemini_json(prompt: str, fallback: Any = None) -> Any:
    """Call Gemini 1.5 Flash and return parsed JSON. Falls back gracefully."""
    model = _get_model()
    if model is None:
        logger.warning("Gemini not configured — returning fallback")
        return fallback
    try:
        response = await asyncio.to_thread(model.generate_content, prompt)
        return json.loads(response.text)
    except Exception as e:
        logger.error(f"Gemini call failed: {e}")
        return fallback


SIGNAL_PROMPT = """You are MarketNerve Signal Scout — an AI analyst covering Indian equities for retail investors.

Stock: {company} ({ticker}) | Sector: {sector}

Market Data (NSE):
- Price: ₹{price:.2f} | Day Change: {day_change_pct:+.2f}%
- Volume: {volume:,} ({volume_ratio:.1f}× 20-day avg)
- RSI(14): {rsi:.1f} | MACD: {macd_signal}
- Above 50-SMA: {above_sma_50} | Above 200-SMA: {above_sma_200}
- 52W Range: ₹{week_52_low:.0f} – ₹{week_52_high:.0f}

Volume Z-Score: {z_score:.2f}σ (>2.0 = significant institutional activity)

Recent Filing/Announcement:
{announcement}

Generate a complete market signal. Return JSON exactly matching:
{{
  "signal_type": "one of: FII Activity | Bulk Deal | Promoter Buy | Volume Anomaly | Technical Breakout | Oversold Bounce | Institutional Accumulation | Momentum Surge",
  "headline": "compelling one-line headline under 80 chars",
  "summary": "2 clear sentences for a retail investor explaining what happened and why it matters",
  "confidence": 0.0-1.0,
  "anomaly_score": 0.0-4.0,
  "z_score": {z_score_val:.2f},
  "reward_risk_ratio": 1.5-4.0,
  "portfolio_impact_pct": 0.5-8.0,
  "reasoning_steps": ["step1", "step2", "step3"],
  "watch_items": ["item1", "item2", "item3"],
  "tags": ["tag1", "tag2"]
}}"""

PORTFOLIO_QA_PROMPT = """You are MarketNerve Portfolio Lens — an expert Indian equities portfolio analyst.

Portfolio Summary:
- Invested: ₹{invested:,.0f} | Current: ₹{current:,.0f}
- XIRR: {xirr:.1f}% | Health Score: {health_score}/100
- Holdings: {holdings_count} positions

Top Holdings:
{holdings_list}

Sector Allocation:
{sector_list}

User Question: {question}

Provide a precise, data-driven answer referencing actual numbers from this portfolio.
Consider: NSE/BSE listed stocks, mutual fund look-through exposures, Indian market context.

Return JSON:
{{
  "answer": "2-3 specific sentences mentioning actual portfolio numbers",
  "logic": ["reasoning step 1", "reasoning step 2", "reasoning step 3"],
  "supporting_metrics": {{"key": "value"}},
  "disclaimer": "short risk disclaimer"
}}"""

PATTERN_NARRATIVE_PROMPT = """You are MarketNerve Pattern Mind — a technical analysis expert for Indian equities.

Stock: {company} ({ticker}) | Sector: {sector}
Pattern Detected: {pattern_type}

Technical Data:
- Price: ₹{price:.2f} | Day Change: {day_change_pct:+.2f}%
- RSI(14): {rsi:.1f}
- Pattern Signal: {pattern_detail}

Historical Backtest (NSE universe, last 3 years):
- Win Rate: {win_rate:.0f}% ({wins}/{occurrences} occurrences)
- Avg 30D Return: {avg_return:+.1f}%

Write a concise, actionable pattern analysis. Return JSON:
{{
  "narrative": "2 sentences: what pattern means + historical context",
  "context": "1 sentence: current market condition context",
  "risk_flags": ["flag1", "flag2"],
  "signal_strength": "High conviction | Actionable | Emerging"
}}"""


async def generate_signal(stock_data: dict, announcement: str = "No significant recent filing.") -> dict | None:
    prompt = SIGNAL_PROMPT.format(
        company=stock_data["company"],
        ticker=stock_data["ticker"],
        sector=stock_data["sector"],
        price=stock_data.get("current_price", 0),
        day_change_pct=stock_data.get("day_change_pct", 0),
        volume=stock_data.get("volume", 0),
        volume_ratio=stock_data.get("volume_ratio", 1.0),
        rsi=stock_data.get("rsi_14", 50),
        macd_signal=stock_data.get("macd_signal", "neutral"),
        above_sma_50=stock_data.get("above_sma_50", False),
        above_sma_200=stock_data.get("above_sma_200", False),
        week_52_high=stock_data.get("week_52_high", 0),
        week_52_low=stock_data.get("week_52_low", 0),
        z_score=stock_data.get("z_score", 0),
        z_score_val=stock_data.get("z_score", 0),
        announcement=announcement,
    )
    return await gemini_json(prompt, fallback=None)


async def generate_pattern_narrative(stock_data: dict, pattern_data: dict) -> dict | None:
    prompt = PATTERN_NARRATIVE_PROMPT.format(
        company=stock_data["company"],
        ticker=stock_data["ticker"],
        sector=stock_data["sector"],
        pattern_type=pattern_data["pattern_type"],
        price=stock_data.get("current_price", 0),
        day_change_pct=stock_data.get("day_change_pct", 0),
        rsi=stock_data.get("rsi_14", 50),
        pattern_detail=pattern_data.get("detail", ""),
        win_rate=pattern_data.get("win_rate", 60),
        wins=pattern_data.get("wins", 6),
        occurrences=pattern_data.get("occurrences", 10),
        avg_return=pattern_data.get("avg_return", 5.0),
    )
    return await gemini_json(prompt, fallback=None)


async def answer_portfolio_question(question: str, portfolio: dict) -> dict:
    holdings = portfolio.get("holdings", [])
    holdings_list = "\n".join(
        f"  {h.get('name', h.get('ticker', '?'))}: ₹{h.get('current_value', 0):,.0f} ({h.get('weight', 0)*100:.1f}%)"
        for h in holdings[:8]
    )
    sectors = portfolio.get("sector_exposure", [])
    sector_list = "\n".join(
        f"  {s['name']}: {s['weight']*100:.1f}%" for s in sectors[:6]
    )
    health = portfolio.get("money_health_score", {})
    prompt = PORTFOLIO_QA_PROMPT.format(
        invested=portfolio.get("invested_amount", 0),
        current=portfolio.get("current_value", 0),
        xirr=portfolio.get("xirr", 0) * 100,
        health_score=health.get("overall", 65) if isinstance(health, dict) else 65,
        holdings_count=len(holdings),
        holdings_list=holdings_list or "  No holdings data",
        sector_list=sector_list or "  No sector data",
        question=question,
    )
    fallback = {
        "answer": "Unable to process question at this time. Please try again.",
        "logic": ["Gemini AI unavailable"],
        "supporting_metrics": {},
        "disclaimer": "Not financial advice.",
    }
    return await gemini_json(prompt, fallback=fallback)
