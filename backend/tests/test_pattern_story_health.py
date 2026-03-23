"""Comprehensive unit tests for Pattern Mind, Story Engine, IPO Intelligence, and Health."""
from __future__ import annotations

import pytest

from app.services.health import get_health
from app.services.ipo import get_ipo_by_name, list_active_ipos
from app.services.patterns import (
    get_live_pattern_events,
    get_pattern_by_id,
    get_ticker_patterns,
    list_patterns,
    list_patterns_by_confidence,
)
from app.services.story import get_latest_video, get_live_filing_events, get_story_arc, list_all_arcs


class TestPatterns:
    def test_all_patterns_have_required_fields(self):
        patterns = list_patterns()
        assert len(patterns) >= 5
        for p in patterns:
            assert p.ticker
            assert p.company
            assert p.sector
            assert p.pattern_type
            assert 0 < p.confidence <= 1.0
            assert p.signal_strength in ("High conviction", "Actionable", "Emerging")
            assert p.narrative
            assert p.context

    def test_patterns_sorted_by_confidence_desc(self):
        patterns = list_patterns()
        for i in range(len(patterns) - 1):
            assert patterns[i].confidence >= patterns[i + 1].confidence

    def test_backtest_wins_plus_losses_equals_occurrences(self):
        patterns = list_patterns()
        for p in patterns:
            assert p.backtest.wins + p.backtest.losses == p.backtest.occurrences

    def test_win_rate_between_zero_and_one(self):
        patterns = list_patterns()
        for p in patterns:
            assert 0.0 <= p.backtest.win_rate <= 1.0

    def test_filter_by_pattern_type_golden_cross(self):
        patterns = list_patterns(pattern_type="Golden Cross")
        assert len(patterns) >= 1
        for p in patterns:
            assert "Golden Cross" in p.pattern_type

    def test_filter_by_ticker_hdfcbank(self):
        patterns = list_patterns(ticker="HDFCBANK")
        assert len(patterns) >= 1
        for p in patterns:
            assert p.ticker == "HDFCBANK"

    def test_filter_by_sector_it(self):
        patterns = list_patterns(sector="Information Technology")
        assert len(patterns) >= 1
        for p in patterns:
            assert p.sector == "Information Technology"

    def test_filter_by_min_confidence(self):
        patterns = list_patterns(min_confidence=0.75)
        for p in patterns:
            assert p.confidence >= 0.75

    def test_high_conviction_signal_strength_label(self):
        patterns = list_patterns(min_confidence=0.80)
        for p in patterns:
            assert p.signal_strength == "High conviction"

    def test_reward_risk_ratio_non_negative(self):
        patterns = list_patterns()
        for p in patterns:
            assert p.backtest.reward_risk_ratio is not None
            assert p.backtest.reward_risk_ratio >= 0


class TestGetPatternById:
    def test_get_pattern_by_valid_id(self):
        p = get_pattern_by_id("pat-hdfcbank-golden-cross")
        assert p.ticker == "HDFCBANK"
        assert p.pattern_type == "Golden Cross"

    def test_get_pattern_by_invalid_id_raises(self):
        with pytest.raises(KeyError):
            get_pattern_by_id("pat-nonexistent-xyz")


class TestGetTickerPatterns:
    def test_ticker_patterns_for_reliance(self):
        patterns = get_ticker_patterns("RELIANCE")
        assert len(patterns) >= 1
        for p in patterns:
            assert p.ticker == "RELIANCE"

    def test_ticker_patterns_for_unknown_ticker_empty(self):
        patterns = get_ticker_patterns("NONEXISTENT")
        assert patterns == []


class TestListPatternsByConfidence:
    def test_high_confidence_filter(self):
        patterns = list_patterns_by_confidence(min_conf=0.76)
        for p in patterns:
            assert p.confidence >= 0.76


class TestLivePatternEvents:
    def test_pattern_events_channel_is_patterns(self):
        events = get_live_pattern_events()
        assert len(events) >= 1
        for e in events:
            assert e.channel == "patterns"
            assert e.event_type == "pattern_detected"

    def test_pattern_events_have_reward_risk_ratio(self):
        events = get_live_pattern_events()
        for e in events:
            assert "reward_risk_ratio" in e.payload


class TestStoryEngine:
    def test_latest_video_has_six_outline_steps(self):
        video = get_latest_video()
        assert len(video.script_outline) >= 6

    def test_latest_video_has_formats(self):
        video = get_latest_video()
        assert len(video.formats) >= 2

    def test_get_story_arc_zomato(self):
        arc = get_story_arc("zomato")
        assert arc.slug == "zomato-profitability-journey"
        assert arc.sentiment
        assert 0 <= arc.sentiment_score <= 1.0
        assert len(arc.what_to_watch_next) >= 2
        assert len(arc.events) >= 3

    def test_get_story_arc_hdfc(self):
        arc = get_story_arc("hdfc")
        assert arc.slug == "hdfc-merger-integration"
        assert len(arc.events) >= 3

    def test_get_story_arc_adani(self):
        arc = get_story_arc("adani")
        assert arc.slug == "adani-group-recovery"

    def test_get_story_arc_fallback_to_first(self):
        arc = get_story_arc("completely-unknown-query")
        # Should return first arc, not raise
        assert arc.slug

    def test_list_all_arcs_returns_five(self):
        arcs = list_all_arcs()
        assert len(arcs) == 5

    def test_all_arcs_have_sentiment_score(self):
        arcs = list_all_arcs()
        for arc in arcs:
            assert 0.0 <= arc.sentiment_score <= 1.0

    def test_all_arcs_have_events(self):
        arcs = list_all_arcs()
        for arc in arcs:
            assert len(arc.events) >= 2


class TestLiveFilingEvents:
    def test_filing_events_channel_is_filings(self):
        events = get_live_filing_events()
        assert len(events) >= 1
        assert all(e.channel == "filings" for e in events)

    def test_filing_events_have_confidence(self):
        events = get_live_filing_events()
        for e in events:
            assert "confidence" in e.payload
            assert "summary" in e.payload


class TestIpoIntelligence:
    def test_active_ipos_returns_four(self):
        ipos = list_active_ipos()
        assert len(ipos) == 4

    def test_ipos_sorted_by_subscription_desc(self):
        ipos = list_active_ipos()
        for i in range(len(ipos) - 1):
            assert ipos[i].subscription_multiple >= ipos[i + 1].subscription_multiple

    def test_ipos_have_demand_label(self):
        ipos = list_active_ipos()
        for ipo in ipos:
            assert ipo.demand_label in ("Hot demand", "Healthy demand", "Measured demand", "Subdued demand")

    def test_ipos_have_risk_level(self):
        ipos = list_active_ipos()
        for ipo in ipos:
            assert ipo.risk_level in ("Aggressive", "Balanced", "Cautious")

    def test_ipos_have_cutoff_price(self):
        ipos = list_active_ipos()
        for ipo in ipos:
            assert ipo.cutoff_price is not None
            assert ipo.cutoff_price > 0

    def test_ipos_have_listing_date(self):
        ipos = list_active_ipos()
        for ipo in ipos:
            assert ipo.listing_date is not None

    def test_hot_demand_label_for_high_subscription(self):
        ipos = list_active_ipos()
        aether = next(ipo for ipo in ipos if "Aether" in ipo.name)
        assert aether.demand_label == "Hot demand"
        assert aether.risk_level == "Aggressive"

    def test_get_ipo_by_name(self):
        ipo = get_ipo_by_name("aether")
        assert "Aether" in ipo.name

    def test_get_ipo_by_name_not_found_raises(self):
        with pytest.raises(KeyError):
            get_ipo_by_name("nonexistentipo")


class TestHealthEndpoint:
    def test_health_status_is_healthy(self):
        health = get_health()
        assert health.status == "healthy"

    def test_health_all_agents_ready(self):
        health = get_health()
        for agent, status in health.agent_status.items():
            assert status == "ready", f"{agent} was not ready: {status}"

    def test_health_has_six_pipeline_statuses(self):
        health = get_health()
        assert "exchange_feed" in health.pipeline_status
        assert "filing_parser" in health.pipeline_status
        assert "story_pipeline" in health.pipeline_status
        assert "ipo_tracker" in health.pipeline_status
        assert "websocket_broadcaster" in health.pipeline_status

    def test_health_has_three_websocket_channels(self):
        health = get_health()
        assert len(health.websocket_channels) == 3
        assert all(c.startswith("ws://") for c in health.websocket_channels)

    def test_health_total_signals_processed(self):
        health = get_health()
        assert health.total_signals_processed > 0

    def test_health_uptime_minutes(self):
        health = get_health()
        assert health.uptime_minutes > 0
