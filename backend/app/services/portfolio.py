"""
Portfolio service — analysis uses seed demo data + Gemini Q&A via AI.
"""
import csv
import io
import math
import statistics
from datetime import date, datetime
from typing import Optional

from app.data.repository import repository
from app.ai.gemini_client import answer_portfolio_question
from app.core.config import settings


async def answer_question(question: str, portfolio: dict) -> dict:
    return await answer_portfolio_question(question, portfolio)


def _parse_holdings(csv_text: str) -> list[dict]:
    """Parse CAMS/Zerodha-style CSV."""
    holdings = []
    try:
        reader = csv.DictReader(io.StringIO(csv_text))
        for row in reader:
            ticker = (row.get("Symbol") or row.get("symbol") or row.get("ISIN", "")).strip()
            invested = float(row.get("InvestedValue") or row.get("invested") or row.get("Amount", 0))
            current = float(row.get("CurrentValue") or row.get("current") or row.get("MarketValue", 0))
            if ticker and current > 0:
                holdings.append({
                    "ticker": ticker,
                    "name": row.get("Name") or row.get("Company") or ticker,
                    "invested": invested,
                    "current_value": current,
                    "weight": 0.0,
                })
    except Exception:
        pass
    return holdings


def parse_holdings(csv_text: str, use_demo_data: bool = False) -> list[dict]:
    """Parse holdings from CSV text only. No seed data."""
    return _parse_holdings(csv_text)


def _compute_totals(holdings: list[dict]) -> tuple[float, float]:
    invested = sum(h.get("invested") or h.get("invested_amount") or h.get("current_value", 0) for h in holdings)
    current = sum(h.get("current_value", 0) for h in holdings)
    return invested, current


def _portfolio_totals(holdings: list[dict]) -> tuple[float, float]:
    return _compute_totals(holdings)


def _xirr(invested: float, current: float, years: float = 2.0) -> float:
    if invested <= 0:
        return 0.0
    ratio = current / invested
    if ratio <= 0:
        return 0.0
    return (ratio ** (1 / years)) - 1


def _approx_xirr(invested: float, current: float) -> float:
    return _xirr(invested, current)


def _benchmark_snapshot(alpha: float = 0.0) -> dict:
    return {"name": "Nifty 50", "p_change": 0.012, "alpha": alpha}


def _sector_exposure(holdings: list[dict]) -> list[dict]:
    sector_map: dict[str, float] = {}
    total = sum(h.get("current_value", 0) for h in holdings)
    for h in holdings:
        sector = h.get("sector", h.get("asset_class", "Other"))
        sector_map[sector] = sector_map.get(sector, 0) + h.get("current_value", 0)
    if total <= 0:
        return []
    return sorted(
        [{"name": k, "weight": round(v / total, 4)} for k, v in sector_map.items()],
        key=lambda x: x["weight"], reverse=True
    )


def _stock_exposure(holdings: list[dict]) -> list[dict]:
    total = sum(h.get("current_value", 0) for h in holdings)
    if total <= 0:
        return []
    return sorted(
        [{"ticker": h.get("ticker") or h.get("symbol", ""), "weight": round(h.get("current_value", 0) / total, 4)} for h in holdings],
        key=lambda x: x["weight"], reverse=True
    )


def _health_score(holdings: list[dict], xirr: float, sector_exp: list[dict]) -> dict:
    top_weight = sector_exp[0]["weight"] if sector_exp else 0
    n = len(holdings)
    diversification = min(100, int(n * 8))
    concentration_risk = max(0, 100 - int(top_weight * 200))
    momentum_alignment = min(100, max(40, int(60 + xirr * 200)))
    profit_quality = min(100, max(50, int(70 + xirr * 100)))
    downside_resilience = min(100, max(40, int(65 - top_weight * 50)))
    liquidity_buffer = 75
    overall = int((diversification + concentration_risk + momentum_alignment + profit_quality + downside_resilience + liquidity_buffer) / 6)
    return {
        "overall": overall,
        "diversification": diversification,
        "momentum_alignment": momentum_alignment,
        "concentration_risk": concentration_risk,
        "profit_quality": profit_quality,
        "downside_resilience": downside_resilience,
        "liquidity_buffer": liquidity_buffer,
    }


def _money_health_score(holdings: list[dict], xirr: float, sector_exp: list[dict]) -> dict:
    return _health_score(holdings, xirr, sector_exp)


def _overlap_matrix(holdings: list[dict]) -> list[dict]:
    """Fund overlap matrix — shows which MF holdings overlap with direct stocks."""
    funds = [h for h in holdings if (h.get("asset_class") or h.get("asset_type")) in ("Mutual Fund", "ETF")]
    direct = {h.get("ticker") or h.get("symbol", "") for h in holdings if (h.get("asset_class") or h.get("asset_type")) not in ("Mutual Fund", "ETF")}
    matrix = []
    for fund in funds:
        fund_holdings = fund.get("underlying_holdings", [])
        overlaps = [
            {"symbol": s, "overlap_weight": round(0.12 * (i + 1), 3)}
            for i, s in enumerate(fund_holdings)
            if s in direct
        ]
        matrix.append({"fund": fund.get("ticker") or fund.get("symbol") or fund.get("name", "Unknown"), "overlaps": overlaps})
    return matrix


from app.models.schemas import PortfolioAnalysisResponse


async def analyze_portfolio(csv_text: str = "", use_demo_data: bool = False) -> PortfolioAnalysisResponse:
    """Analyze portfolio from CSV upload. No seed data for live-only mode."""
    holdings = []
    
    if csv_text.strip():
        holdings = _parse_holdings(csv_text)
    
    # For live-only mode: return empty portfolio if no CSV provided
    # Users must upload their portfolio CSV for analysis
    if not holdings:
        return PortfolioAnalysisResponse(
            invested_amount=0.0,
            current_value=0.0,
            absolute_gain=0.0,
            absolute_return=0.0,
            xirr=0.0,
            money_health_score={"overall": 0, "diversification": 0, "momentum_alignment": 0, "concentration_risk": 0, "profit_quality": 0, "downside_resilience": 0, "liquidity_buffer": 0},
            sector_exposure=[],
            stock_exposure=[],
            holdings=[],
            overlap_matrix=[],
            risk_flags=[],
            recommended_actions=["Upload a portfolio CSV file (CAMS/Zerodha format) to analyze your holdings"],
            benchmark_snapshot={"name": "Nifty 50", "p_change": 0.0},
            etf_weight=0.0,
            holdings_count=0
        )

    total = sum(h.get("current_value", 0) for h in holdings)
    for h in holdings:
        h["weight"] = round(h["current_value"] / total, 4) if total > 0 else 0

    invested, current = _compute_totals(holdings)
    xirr = _xirr(invested, current)
    sector_exp = _sector_exposure(holdings)
    health = _health_score(holdings, xirr, sector_exp)
    overlap = _overlap_matrix(holdings)

    pnl = current - invested
    pnl_pct = (pnl / invested * 100) if invested > 0 else 0

    return PortfolioAnalysisResponse(
        invested_amount=round(invested, 2),
        current_value=round(current, 2),
        absolute_gain=round(pnl, 2),
        absolute_return=round(pnl_pct, 2),
        xirr=round(xirr, 4),
        money_health_score=health,
        sector_exposure=sector_exp,
        stock_exposure=_stock_exposure(holdings),
        holdings=holdings,
        overlap_matrix=overlap,
        risk_flags=[],
        recommended_actions=["Monitor your portfolio allocation", "Rebalance if sector exposure exceeds 40%"],
        benchmark_snapshot={"name": "Nifty 50", "p_change": 0.012},
        etf_weight=sum(h.get("current_value", 0) for h in holdings if (h.get("asset_class") or h.get("asset_type")) in ("ETF", "Index Fund")) / current if current > 0 else 0,
        holdings_count=len(holdings)
    )


async def answer_question(question: str, portfolio: dict) -> dict:
    """Use Gemini to answer portfolio questions."""
    if hasattr(portfolio, "model_dump"):
        portfolio = portfolio.model_dump()

    if settings.has_ai:
        return await answer_portfolio_question(question, portfolio)
    # Simplified fallback routing if Gemini not available
    q = question.lower()
    seed = await repository.get_portfolio()
    qa = seed.get("qa_pairs", [])
    for pair in qa:
        if any(kw in q for kw in pair.get("keywords", [])):
            return {
                "answer": pair.get("answer", ""),
                "logic": pair.get("logic", []),
                "supporting_metrics": pair.get("supporting_metrics", {}),
                "disclaimer": "Historical data only. Not investment advice.",
            }
    return {
        "answer": "Ask me about your sector exposure, overlap with mutual funds, HDFC Bank exposure, rate sensitivity, or XIRR.",
        "logic": ["Question routing unavailable without Gemini AI."],
        "supporting_metrics": {},
        "disclaimer": "Not financial advice.",
    }
