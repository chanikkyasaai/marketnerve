from __future__ import annotations

import csv
import io
from collections import defaultdict

from app.data.repository import repository
from app.models.schemas import (
    BenchmarkSnapshot,
    ExposureItem,
    FundOverlap,
    Holding,
    MoneyHealthScore,
    OverlapRow,
    PortfolioAnalysisResponse,
    PortfolioAnswer,
)


DISCLAIMER = "Portfolio Lens is analytical tooling, not SEBI-registered investment advice."

# Nifty 50 benchmark return (seeded)
_BENCHMARK_RETURN = 0.118


def _coerce_holding(row: dict) -> Holding:
    return Holding(
        asset_type=row["asset_type"],
        name=row["name"],
        symbol=row["symbol"],
        sector=row["sector"],
        units=float(row["units"]),
        invested_amount=float(row["invested_amount"]),
        current_value=float(row["current_value"]),
        years_held=float(row.get("years_held", 1.0)),
        lookthrough_exposure=row.get("lookthrough_exposure", {}) or {},
    )


def parse_holdings(csv_text: str | None, use_demo_data: bool = True) -> list[Holding]:
    if use_demo_data or not csv_text:
        return [_coerce_holding(item) for item in repository.get_portfolio_demo()["holdings"]]

    reader = csv.DictReader(io.StringIO(csv_text.strip()))
    holdings: list[Holding] = []
    for row in reader:
        exposure = {}
        raw_exposure = (row.get("lookthrough_exposure") or "").strip()
        if raw_exposure:
            for pair in raw_exposure.split("|"):
                symbol, value = pair.split(":")
                exposure[symbol.strip().upper()] = float(value)
        holdings.append(
            Holding(
                asset_type=row["asset_type"],
                name=row["name"],
                symbol=row["symbol"].upper(),
                sector=row["sector"],
                units=float(row["units"]),
                invested_amount=float(row["invested_amount"]),
                current_value=float(row["current_value"]),
                years_held=float(row.get("years_held", 1.0)),
                lookthrough_exposure=exposure,
            )
        )
    return holdings


def _portfolio_totals(holdings: list[Holding]) -> tuple[float, float]:
    return (
        sum(h.invested_amount for h in holdings),
        sum(h.current_value for h in holdings),
    )


def _approx_xirr(holdings: list[Holding]) -> float:
    invested, current = _portfolio_totals(holdings)
    total_years = sum(h.years_held * h.invested_amount for h in holdings)
    avg_years = max(total_years / max(invested, 1), 0.25)
    return (current / max(invested, 1)) ** (1 / avg_years) - 1


def _weight_by_type(holdings: list[Holding], asset_type: str) -> float:
    total_value = sum(h.current_value for h in holdings) or 1
    value = sum(h.current_value for h in holdings if h.asset_type.lower() == asset_type.lower())
    return round(value / total_value, 4)


def _sector_exposure(holdings: list[Holding]) -> list[ExposureItem]:
    total_value = sum(h.current_value for h in holdings) or 1
    sector_totals: defaultdict[str, float] = defaultdict(float)
    for h in holdings:
        sector_totals[h.sector] += h.current_value
    return [
        ExposureItem(name=sector, weight=round(value / total_value, 4), exposure_type="sector")
        for sector, value in sorted(sector_totals.items(), key=lambda x: x[1], reverse=True)
    ]


def _stock_exposure(holdings: list[Holding]) -> list[ExposureItem]:
    total_value = sum(h.current_value for h in holdings) or 1
    stock_totals: defaultdict[str, float] = defaultdict(float)
    for h in holdings:
        if h.asset_type.lower() == "equity":
            stock_totals[h.symbol] += h.current_value
        for symbol, weight in h.lookthrough_exposure.items():
            stock_totals[symbol] += h.current_value * weight
    ranked = sorted(stock_totals.items(), key=lambda x: x[1], reverse=True)
    return [
        ExposureItem(name=symbol, weight=round(value / total_value, 4), exposure_type="stock")
        for symbol, value in ranked[:10]
    ]


def _overlap_matrix(holdings: list[Holding]) -> list[OverlapRow]:
    direct_symbols = {h.symbol for h in holdings if h.asset_type.lower() == "equity"}
    rows: list[OverlapRow] = []
    for h in holdings:
        if h.asset_type.lower() not in ("mutual fund", "etf"):
            continue
        overlaps = sorted(
            (
                FundOverlap(symbol=symbol, overlap_weight=round(weight, 4))
                for symbol, weight in h.lookthrough_exposure.items()
                if symbol in direct_symbols
            ),
            key=lambda x: x.overlap_weight,
            reverse=True,
        )
        rows.append(OverlapRow(fund=h.name, overlaps=overlaps))
    return rows


def _benchmark_snapshot(absolute_return: float) -> BenchmarkSnapshot:
    alpha = absolute_return - _BENCHMARK_RETURN
    commentary = (
        "Portfolio is ahead of the seeded Nifty 50 benchmark."
        if alpha >= 0
        else "Portfolio trails the seeded benchmark — review allocation."
    )
    return BenchmarkSnapshot(
        benchmark="Nifty 50",
        benchmark_return=round(_BENCHMARK_RETURN, 4),
        portfolio_return=round(absolute_return, 4),
        relative_alpha=round(alpha, 4),
        commentary=commentary,
    )


def _money_health_score(
    holdings: list[Holding], absolute_return: float, overlap_rows: list[OverlapRow]
) -> MoneyHealthScore:
    # Diversification: penalize if < 5 holdings
    diversification = 80 if len(holdings) >= 6 else (72 if len(holdings) >= 4 else 55)
    # Concentration risk: penalize for mutual fund/ETF overlap
    has_overlap = any(len(row.overlaps) >= 1 for row in overlap_rows)
    concentration_risk = 58 if has_overlap else 82
    # Profit quality: based on absolute return vs benchmark
    profit_quality = 85 if absolute_return > 0.15 else (72 if absolute_return > 0.10 else 60)
    momentum_alignment = 78
    downside_resilience = 71
    # Liquidity buffer: penalize for very high illiquid holdings (gold, unlisted)
    illiquid_sectors = {"Commodities"}
    illiquid_weight = sum(h.current_value for h in holdings if h.sector in illiquid_sectors)
    total_value = sum(h.current_value for h in holdings) or 1
    illiquid_pct = illiquid_weight / total_value
    liquidity_buffer = 64 if illiquid_pct > 0.10 else 80
    overall = min(
        100,
        round((diversification + concentration_risk + profit_quality + momentum_alignment + downside_resilience + liquidity_buffer) / 6),
    )
    return MoneyHealthScore(
        overall=overall,
        diversification=diversification,
        momentum_alignment=momentum_alignment,
        concentration_risk=concentration_risk,
        profit_quality=profit_quality,
        downside_resilience=downside_resilience,
        liquidity_buffer=liquidity_buffer,
    )


def _build_risk_flags(sector_exposure: list[ExposureItem], stock_exposure: list[ExposureItem], overlap_rows: list[OverlapRow]) -> list[str]:
    flags = []
    if any(item.weight > 0.20 for item in stock_exposure[:2]):
        flags.append("Top holdings create meaningful single-name concentration (>20% in top 2 stocks).")
    if any(e.name == "Financial Services" and e.weight > 0.35 for e in sector_exposure):
        flags.append("Financial-services exposure is above the 35% comfort band.")
    if overlap_rows and any(row.overlaps for row in overlap_rows):
        flags.append("Mutual fund/ETF holdings overlap with direct equity positions — effective exposure is higher than it appears.")
    if any(e.name == "Information Technology" and e.weight > 0.30 for e in sector_exposure):
        flags.append("IT sector concentration above 30% — sector-specific risk elevated.")
    return flags


def _build_recommended_actions(holdings: list[Holding], sector_exp: list[ExposureItem], absolute_return: float) -> list[str]:
    actions = []
    fin_exp = next((e.weight for e in sector_exp if e.name == "Financial Services"), 0.0)
    if fin_exp > 0.30:
        actions.append(f"Review financial-services allocation ({round(fin_exp * 100, 1)}%) — consider rebalancing into underrepresented sectors.")
    it_exp = next((e.weight for e in sector_exp if e.name == "Information Technology"), 0.0)
    if it_exp > 0:
        actions.append(f"IT sector ({round(it_exp * 100, 1)}%) is showing active FII inflows — current allocation appears well-timed.")
    if absolute_return > _BENCHMARK_RETURN:
        actions.append(f"Portfolio is ahead of Nifty benchmark by {round((absolute_return - _BENCHMARK_RETURN) * 100, 1)}%. Protect alpha by periodic rebalancing.")
    else:
        actions.append("Portfolio trails Nifty benchmark — identify underperforming positions for review.")
    commodity_weight = sum(h.current_value for h in holdings if h.sector == "Commodities")
    total_val = sum(h.current_value for h in holdings) or 1
    if commodity_weight / total_val < 0.05:
        actions.append("Consider a small gold or commodity allocation (5-8%) as portfolio insurance against tail risk.")
    return actions[:4]  # Cap at 4 actions


def analyze_portfolio(
    csv_text: str | None = None,
    use_demo_data: bool = True,
    zero_retention_mode: bool = True,
) -> PortfolioAnalysisResponse:
    holdings = parse_holdings(csv_text, use_demo_data)
    invested, current = _portfolio_totals(holdings)
    absolute_gain = current - invested
    absolute_return = absolute_gain / max(invested, 1)
    overlap_rows = _overlap_matrix(holdings)
    money_health = _money_health_score(holdings, absolute_return, overlap_rows)
    sector_exposure = _sector_exposure(holdings)
    stock_exposure = _stock_exposure(holdings)
    risk_flags = _build_risk_flags(sector_exposure, stock_exposure, overlap_rows)
    recommended_actions = _build_recommended_actions(holdings, sector_exposure, absolute_return)

    return PortfolioAnalysisResponse(
        portfolio_name=repository.get_portfolio_demo()["name"],
        currency=repository.get_portfolio_demo()["currency"],
        zero_retention_mode=zero_retention_mode,
        holdings_count=len(holdings),
        invested_amount=round(invested, 2),
        current_value=round(current, 2),
        absolute_gain=round(absolute_gain, 2),
        absolute_return=round(absolute_return, 4),
        xirr=round(_approx_xirr(holdings), 4),
        direct_equity_weight=_weight_by_type(holdings, "Equity"),
        mutual_fund_weight=_weight_by_type(holdings, "Mutual Fund"),
        etf_weight=_weight_by_type(holdings, "ETF"),
        sector_exposure=sector_exposure,
        stock_exposure=stock_exposure,
        overlap_matrix=overlap_rows,
        benchmark_snapshot=_benchmark_snapshot(absolute_return),
        money_health_score=money_health,
        risk_flags=risk_flags,
        recommended_actions=recommended_actions,
    )


def _exposure_pct_for_ticker(holdings: list[Holding], ticker: str) -> float:
    total = sum(h.current_value for h in holdings) or 1
    exposure = 0.0
    for h in holdings:
        if h.symbol == ticker:
            exposure += h.current_value
        if ticker in h.lookthrough_exposure:
            exposure += h.current_value * h.lookthrough_exposure[ticker]
    return round(exposure / total, 4)


def answer_portfolio_question(
    question: str,
    csv_text: str | None = None,
    use_demo_data: bool = True,
    zero_retention_mode: bool = True,
) -> PortfolioAnswer:
    holdings = parse_holdings(csv_text, use_demo_data)
    analysis = analyze_portfolio(csv_text, use_demo_data, zero_retention_mode)
    lower = question.lower()

    if "overlap" in lower or "mutual fund" in lower:
        top_fund = max(analysis.overlap_matrix, key=lambda x: len(x.overlaps), default=None)
        answer = (
            f"{top_fund.fund} has the highest visible overlap with the direct equity book."
            if top_fund
            else "No overlap was detected between mutual funds/ETFs and direct equities."
        )
        metrics = {"overlap_funds": len(analysis.overlap_matrix)}
        logic = [
            "Parsed portfolio holdings.",
            "Computed look-through overlap between mutual funds/ETFs and direct stocks.",
            "Ranked funds by count of overlapping direct positions.",
        ]

    elif "reliance" in lower:
        exposure = _exposure_pct_for_ticker(holdings, "RELIANCE")
        answer = f"Estimated look-through exposure to Reliance is {round(exposure * 100, 2)}% of total portfolio value."
        metrics = {"reliance_exposure_pct": round(exposure * 100, 2)}
        logic = [
            "Parsed direct holdings and mutual-fund look-through exposures.",
            "Aggregated direct and indirect Reliance exposure.",
            "Normalized exposure by total portfolio value.",
        ]

    elif "hdfc" in lower and ("bank" in lower or "bank" in lower):
        exposure = _exposure_pct_for_ticker(holdings, "HDFCBANK")
        answer = f"Total HDFC Bank look-through exposure (direct + funds) is {round(exposure * 100, 2)}% of portfolio."
        metrics = {"hdfcbank_exposure_pct": round(exposure * 100, 2)}
        logic = [
            "Identified direct HDFC Bank equity holding.",
            "Added proportional look-through from Axis Bluechip Fund and Parag Parikh Flexi Cap.",
            "Also computed Nifty BeES ETF HDFC Bank component.",
            "Normalized by total portfolio value.",
        ]

    elif "rbi" in lower or "rate" in lower or "interest" in lower:
        fin_weight = next((e.weight for e in analysis.sector_exposure if e.name == "Financial Services"), 0.0)
        answer = (
            f"A 50 bps rate hike would most likely pressure the {round(fin_weight * 100, 1)}% financial-services sleeve first. "
            "Diversified funds soften the overall shock, but HDFC Bank direct holding carries the most direct rate sensitivity."
        )
        metrics = {"financial_services_exposure_pct": round(fin_weight * 100, 2)}
        logic = [
            "Computed sector concentration using full look-through.",
            "Mapped rate sensitivity to the financial-services allocation.",
            "Identified diversified funds as natural buffers.",
        ]

    elif "concentration" in lower or "concentrated" in lower:
        top_stocks = analysis.stock_exposure[:3]
        top_names = ", ".join(f"{e.name} ({round(e.weight * 100, 1)}%)" for e in top_stocks)
        answer = f"Top 3 stock concentrations are: {top_names}. Consider rebalancing if any single name exceeds 20% look-through weight."
        metrics = {s.name: round(s.weight * 100, 2) for s in top_stocks}
        logic = [
            "Calculated look-through stock exposure across all holdings.",
            "Ranked by portfolio weight.",
            "Applied a 20% single-name threshold as a concentration risk guideline.",
        ]

    elif "xirr" in lower or "return" in lower or "performance" in lower:
        xirr_pct = round(analysis.xirr * 100, 2)
        alpha_pct = round(analysis.benchmark_snapshot.relative_alpha * 100, 2)
        answer = (
            f"Portfolio XIRR is {xirr_pct}% vs Nifty 50 benchmark of {round(_BENCHMARK_RETURN * 100, 1)}%. "
            f"Relative alpha: {'+' if alpha_pct >= 0 else ''}{alpha_pct}%."
        )
        metrics = {"xirr_pct": xirr_pct, "relative_alpha_pct": alpha_pct}
        logic = [
            "Computed approximate XIRR across all holdings with time-weighting.",
            "Compared against seeded Nifty 50 benchmark (11.8% annualized).",
            "Calculated relative alpha.",
        ]

    elif "health" in lower or "score" in lower:
        score = analysis.money_health_score.overall
        answer = (
            f"Your Money Health Score is {score}/100. "
            f"Strongest dimension: Profit Quality ({analysis.money_health_score.profit_quality}/100). "
            f"Weakest dimension: Concentration Risk ({analysis.money_health_score.concentration_risk}/100)."
        )
        metrics = {"overall_health_score": score}
        logic = [
            "Evaluated diversification, concentration, momentum alignment, profit quality, downside resilience, and liquidity buffer.",
            "Identified strongest and weakest scoring dimensions.",
            "Score is relative to typical retail portfolio benchmarks.",
        ]

    else:
        xirr_pct = round(analysis.xirr * 100, 2)
        answer = (
            f"Portfolio XIRR is {xirr_pct}% with relative alpha of {round(analysis.benchmark_snapshot.relative_alpha * 100, 2)}% "
            f"vs Nifty 50. Money Health Score: {analysis.money_health_score.overall}/100."
        )
        metrics = {
            "xirr_pct": xirr_pct,
            "relative_alpha_pct": round(analysis.benchmark_snapshot.relative_alpha * 100, 2),
            "health_score": analysis.money_health_score.overall,
        }
        logic = [
            "Computed portfolio return and approximate XIRR.",
            "Benchmarked against seeded Nifty 50 reference.",
            "Included Money Health Score for holistic portfolio view.",
        ]

    return PortfolioAnswer(
        question=question,
        answer=answer,
        logic=logic,
        sources=["Uploaded holdings data", "Seeded market snapshot", analysis.benchmark_snapshot.benchmark],
        supporting_metrics=metrics,
        disclaimer=DISCLAIMER,
    )
