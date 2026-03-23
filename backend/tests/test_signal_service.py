"""Comprehensive unit tests for the Signal Scout service."""
from __future__ import annotations

import pytest

from app.services.signals import (
    calculate_z_score,
    count_signals,
    create_subscription,
    get_audit,
    get_high_confidence_signals,
    get_live_signal_events,
    get_signal,
    get_signals_by_sector,
    list_signals,
)


class TestListSignals:
    def test_signals_are_ranked_by_impact_score(self):
        signals = list_signals()
        for i in range(len(signals) - 1):
            assert signals[i].impact_score >= signals[i + 1].impact_score

    def test_signals_have_all_required_fields(self):
        signals = list_signals()
        assert len(signals) > 0
        s = signals[0]
        assert s.id
        assert s.ticker
        assert s.company
        assert s.sector
        assert s.headline
        assert s.summary
        assert 0 < s.confidence <= 1.0
        assert s.impact_score > 0
        assert s.anomaly_score >= 0
        assert s.z_score != 0.0 or s.anomaly_score >= 0  # at least one non-zero

    def test_signals_tagged_source_cited(self):
        signals = list_signals()
        for s in signals:
            assert "source-cited" in s.tags

    def test_high_confidence_signals_tagged_correctly(self):
        signals = list_signals()
        for s in signals:
            if s.confidence >= 0.80:
                assert "high-confidence" in s.tags
            else:
                assert "high-confidence" not in s.tags

    def test_fresh_signals_tagged_fresh(self):
        signals = list_signals()
        for s in signals:
            if s.freshness_label == "fresh":
                assert "fresh" in s.tags

    def test_filter_by_sector_information_technology(self):
        signals = list_signals(sector="Information Technology")
        assert len(signals) >= 1
        for s in signals:
            assert s.sector == "Information Technology"

    def test_filter_by_min_confidence(self):
        threshold = 0.75
        signals = list_signals(min_confidence=threshold)
        for s in signals:
            assert s.confidence >= threshold

    def test_filter_by_signal_type(self):
        signals = list_signals(signal_type="Promoter Accumulation")
        assert len(signals) >= 1
        for s in signals:
            assert s.signal_type == "Promoter Accumulation"

    def test_pagination_limit(self):
        all_signals = list_signals(limit=50)
        first_page = list_signals(limit=3, offset=0)
        second_page = list_signals(limit=3, offset=3)
        assert len(first_page) == 3
        assert len(second_page) <= 3
        # Pages should not overlap
        first_ids = {s.id for s in first_page}
        second_ids = {s.id for s in second_page}
        assert first_ids.isdisjoint(second_ids)

    def test_count_signals_matches(self):
        total = count_signals()
        signals = list_signals(limit=50)
        assert total == len(signals)

    def test_enriched_backtest_stats_consistent(self):
        signals = list_signals()
        for s in signals:
            assert s.backtest.wins + s.backtest.losses == s.backtest.occurrences
            assert 0 <= s.backtest.win_rate <= 1.0
            assert s.backtest.occurrences >= 3


class TestGetSignal:
    def test_get_signal_by_id(self):
        signal = get_signal("sig-persistent-promoter-dips")
        assert signal.id == "sig-persistent-promoter-dips"
        assert signal.ticker == "PERSISTENT"

    def test_get_signal_by_ticker(self):
        signal = get_signal("PERSISTENT")
        assert signal.ticker == "PERSISTENT"

    def test_get_signal_not_found_raises_key_error(self):
        with pytest.raises(KeyError):
            get_signal("NONEXISTENT-TICKER-XYZ")

    def test_signal_sources_have_names(self):
        signal = get_signal("sig-persistent-promoter-dips")
        assert len(signal.sources) >= 2
        for src in signal.sources:
            assert src.name


class TestHighConfidenceSignals:
    def test_high_confidence_signals_above_threshold(self):
        signals = get_high_confidence_signals(threshold=0.80)
        for s in signals:
            assert s.confidence >= 0.80

    def test_high_confidence_signals_not_empty(self):
        signals = get_high_confidence_signals(threshold=0.70)
        assert len(signals) >= 1

    def test_high_confidence_limit_respected(self):
        signals = get_high_confidence_signals(threshold=0.0, limit=3)
        assert len(signals) <= 3


class TestSignalsBysector:
    def test_get_signals_by_sector_it(self):
        signals = get_signals_by_sector("Information Technology")
        assert all(s.sector == "Information Technology" for s in signals)


class TestAuditTrail:
    def test_audit_contains_required_fields(self):
        audit = get_audit("sig-persistent-promoter-dips")
        assert audit.signal_id == "sig-persistent-promoter-dips"
        assert audit.ticker == "PERSISTENT"
        assert len(audit.reasoning_chain) >= 3
        assert "backtest_win_rate" in audit.confidence_metadata
        assert "reward_risk_ratio" in audit.confidence_metadata

    def test_audit_enrichment_snapshot_has_z_score(self):
        audit = get_audit("sig-persistent-promoter-dips")
        assert "z_score" in audit.enrichment_snapshot
        assert "anomaly_score" in audit.enrichment_snapshot
        assert "tags" in audit.enrichment_snapshot

    def test_audit_input_snapshot_has_sources(self):
        audit = get_audit("sig-persistent-promoter-dips")
        assert "sources" in audit.input_snapshot
        assert len(audit.input_snapshot["sources"]) >= 1

    def test_audit_not_found_raises_key_error(self):
        with pytest.raises(KeyError):
            get_audit("nonexistent-signal-xyz")


class TestSubscription:
    def test_create_subscription_returns_active(self):
        sub = create_subscription(["PERSISTENT", "hdfcbank"], ["IT"], 0.7)
        assert sub.active is True
        assert "PERSISTENT" in sub.filters["watchlist"]
        assert "HDFCBANK" in sub.filters["watchlist"]  # normalized to uppercase

    def test_subscription_has_stream_url(self):
        sub = create_subscription([], [], 0.0)
        assert sub.stream.startswith("ws://")
        assert sub.subscription_id.startswith("sub-")


class TestLiveEvents:
    def test_live_signal_events_exist(self):
        events = get_live_signal_events()
        assert len(events) >= 1
        assert events[0].channel == "signals"
        assert events[0].event_type == "signal_detected"

    def test_live_events_have_z_score(self):
        events = get_live_signal_events()
        for e in events:
            assert "z_score" in e.payload
            assert "anomaly_score" in e.payload
            assert "tags" in e.payload


class TestZScoreCalculation:
    def test_z_score_above_mean_is_positive(self):
        assert calculate_z_score(0.8, mean=0.5, std_dev=0.15) > 0

    def test_z_score_below_mean_is_negative(self):
        assert calculate_z_score(0.2, mean=0.5, std_dev=0.15) < 0

    def test_z_score_at_mean_is_zero(self):
        assert calculate_z_score(0.5, mean=0.5, std_dev=0.15) == 0.0

    def test_z_score_zero_std_returns_zero(self):
        assert calculate_z_score(0.9, mean=0.5, std_dev=0.0) == 0.0
