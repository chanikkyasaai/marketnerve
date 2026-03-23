"""Comprehensive unit tests for the Portfolio Lens service."""
from __future__ import annotations

import pytest

from app.services.portfolio import (
    _approx_xirr,
    _benchmark_snapshot,
    _money_health_score,
    _overlap_matrix,
    _portfolio_totals,
    _sector_exposure,
    _stock_exposure,
    analyze_portfolio,
    answer_portfolio_question,
    parse_holdings,
)


CSV_SINGLE_EQUITY = "\n".join([
    "asset_type,name,symbol,sector,units,invested_amount,current_value,years_held,lookthrough_exposure",
    "Equity,Test Corp,TESTCORP,Technology,10,10000,12000,2.0,",
])

CSV_MIXED = "\n".join([
    "asset_type,name,symbol,sector,units,invested_amount,current_value,years_held,lookthrough_exposure",
    "Equity,HDFC Bank,HDFCBANK,Financial Services,15,24000,27150,2.2,",
    "Mutual Fund,Sample Fund,SAMPLE,Diversified,10,1000,1200,1.5,HDFCBANK:0.1|RELIANCE:0.08",
])


class TestParseHoldings:
    def test_demo_data_returns_eight_holdings(self):
        holdings = parse_holdings(None, use_demo_data=True)
        assert len(holdings) == 8

    def test_csv_parsing_basic_row(self):
        holdings = parse_holdings(CSV_SINGLE_EQUITY, use_demo_data=False)
        assert len(holdings) == 1
        assert holdings[0].symbol == "TESTCORP"
        assert holdings[0].current_value == 12000

    def test_csv_parsing_lookthrough_exposure(self):
        holdings = parse_holdings(CSV_MIXED, use_demo_data=False)
        fund = next(h for h in holdings if h.asset_type == "Mutual Fund")
        assert fund.lookthrough_exposure["HDFCBANK"] == 0.1
        assert fund.lookthrough_exposure["RELIANCE"] == 0.08

    def test_csv_parsing_symbol_uppercased(self):
        csv = "\n".join([
            "asset_type,name,symbol,sector,units,invested_amount,current_value,years_held,lookthrough_exposure",
            "Equity,Test Corp,testcorp,Technology,10,10000,12000,2.0,",
        ])
        holdings = parse_holdings(csv, use_demo_data=False)
        assert holdings[0].symbol == "TESTCORP"


class TestPortfolioTotals:
    def test_totals_correct(self):
        holdings = parse_holdings(None, use_demo_data=True)
        invested, current = _portfolio_totals(holdings)
        assert invested > 0
        assert current > invested  # demo portfolio has gains

    def test_single_holding_totals(self):
        holdings = parse_holdings(CSV_SINGLE_EQUITY, use_demo_data=False)
        invested, current = _portfolio_totals(holdings)
        assert invested == 10000
        assert current == 12000


class TestXirr:
    def test_xirr_positive_for_gain_portfolio(self):
        holdings = parse_holdings(None, use_demo_data=True)
        xirr = _approx_xirr(holdings)
        assert xirr > 0

    def test_xirr_reasonable_range(self):
        holdings = parse_holdings(None, use_demo_data=True)
        xirr = _approx_xirr(holdings)
        # Expect between 0% and 40% annualized
        assert 0 < xirr < 0.40


class TestSectorExposure:
    def test_sector_exposure_sums_to_one(self):
        holdings = parse_holdings(None, use_demo_data=True)
        exposures = _sector_exposure(holdings)
        total = sum(e.weight for e in exposures)
        assert abs(total - 1.0) < 0.01  # Allow tiny float precision error

    def test_sector_exposure_has_financial_services(self):
        holdings = parse_holdings(None, use_demo_data=True)
        exposures = _sector_exposure(holdings)
        sectors = [e.name for e in exposures]
        assert "Financial Services" in sectors

    def test_sector_exposure_sorted_by_weight(self):
        holdings = parse_holdings(None, use_demo_data=True)
        exposures = _sector_exposure(holdings)
        for i in range(len(exposures) - 1):
            assert exposures[i].weight >= exposures[i + 1].weight


class TestStockExposure:
    def test_stock_exposure_has_hdfcbank(self):
        holdings = parse_holdings(None, use_demo_data=True)
        exposures = _stock_exposure(holdings)
        symbols = [e.name for e in exposures]
        assert "HDFCBANK" in symbols

    def test_stock_exposure_ranked_by_weight(self):
        holdings = parse_holdings(None, use_demo_data=True)
        exposures = _stock_exposure(holdings)
        for i in range(len(exposures) - 1):
            assert exposures[i].weight >= exposures[i + 1].weight

    def test_stock_exposure_max_10_items(self):
        holdings = parse_holdings(None, use_demo_data=True)
        exposures = _stock_exposure(holdings)
        assert len(exposures) <= 10


class TestOverlapMatrix:
    def test_overlap_matrix_detects_mutual_fund_overlap(self):
        holdings = parse_holdings(None, use_demo_data=True)
        rows = _overlap_matrix(holdings)
        assert len(rows) > 0  # Demo has mutual funds

    def test_overlap_matrix_finds_hdfcbank_overlap(self):
        holdings = parse_holdings(None, use_demo_data=True)
        rows = _overlap_matrix(holdings)
        all_overlapping_symbols = [o.symbol for row in rows for o in row.overlaps]
        # HDFCBANK is direct AND in mutual fund look-through
        assert "HDFCBANK" in all_overlapping_symbols


class TestMoneyHealthScore:
    def test_health_score_overall_in_range(self):
        holdings = parse_holdings(None, use_demo_data=True)
        _, current = _portfolio_totals(holdings)
        invested, _ = _portfolio_totals(holdings)
        overlap = _overlap_matrix(holdings)
        health = _money_health_score(holdings, (current - invested) / invested, overlap)
        assert 0 <= health.overall <= 100

    def test_health_score_all_dimensions_in_range(self):
        holdings = parse_holdings(None, use_demo_data=True)
        invested, current = _portfolio_totals(holdings)
        overlap = _overlap_matrix(holdings)
        health = _money_health_score(holdings, (current - invested) / invested, overlap)
        dimensions = [health.diversification, health.momentum_alignment, health.concentration_risk,
                      health.profit_quality, health.downside_resilience, health.liquidity_buffer]
        for dim in dimensions:
            assert 0 <= dim <= 100


class TestBenchmarkSnapshot:
    def test_positive_alpha_produces_positive_commentary(self):
        snap = _benchmark_snapshot(0.15)
        assert "ahead" in snap.commentary.lower()
        assert snap.relative_alpha > 0

    def test_negative_alpha_produces_trail_commentary(self):
        snap = _benchmark_snapshot(0.05)
        assert "trails" in snap.commentary.lower()
        assert snap.relative_alpha < 0


class TestAnalyzePortfolio:
    def test_demo_portfolio_analysis_complete(self):
        analysis = analyze_portfolio()
        assert analysis.holdings_count == 8
        assert analysis.current_value > analysis.invested_amount
        assert analysis.money_health_score.overall > 0
        assert len(analysis.sector_exposure) >= 3
        assert len(analysis.stock_exposure) >= 3
        assert analysis.zero_retention_mode is True
        assert analysis.etf_weight >= 0

    def test_portfolio_risk_flags_exist(self):
        analysis = analyze_portfolio()
        # Demo portfolio has overlapping holdings
        assert len(analysis.risk_flags) >= 1

    def test_recommended_actions_exist(self):
        analysis = analyze_portfolio()
        assert len(analysis.recommended_actions) >= 1


class TestAnswerPortfolioQuestion:
    def test_overlap_question_routed_correctly(self):
        resp = answer_portfolio_question("Which of my mutual funds overlap most with my direct equity holdings?")
        assert "overlap" in resp.question.lower()
        assert "book" in resp.answer.lower() or "detected" in resp.answer.lower() or "highest" in resp.answer.lower()
        assert len(resp.logic) >= 3
        assert resp.disclaimer

    def test_reliance_question_routed_correctly(self):
        resp = answer_portfolio_question("What is my total Reliance exposure?")
        assert "reliance" in resp.answer.lower()
        assert "reliance_exposure_pct" in resp.supporting_metrics

    def test_hdfc_bank_question_routed_correctly(self):
        resp = answer_portfolio_question("How much HDFC Bank exposure do I have?")
        assert "hdfcbank_exposure_pct" in resp.supporting_metrics

    def test_rate_question_routed_correctly(self):
        resp = answer_portfolio_question("What happens to my portfolio if RBI raises interest rates?")
        assert "financial" in resp.answer.lower() or "rate" in resp.answer.lower()
        assert "financial_services_exposure_pct" in resp.supporting_metrics

    def test_concentration_question_routed_correctly(self):
        resp = answer_portfolio_question("How concentrated is my portfolio?")
        assert len(resp.supporting_metrics) >= 1

    def test_xirr_question_routed_correctly(self):
        resp = answer_portfolio_question("What is my portfolio return?")
        assert "xirr_pct" in resp.supporting_metrics

    def test_health_score_question_routed(self):
        resp = answer_portfolio_question("What is my portfolio health score?")
        assert "overall_health_score" in resp.supporting_metrics
