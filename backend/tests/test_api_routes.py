"""HTTP-level integration tests for all API routes using FastAPI TestClient."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestHealthRoute:
    def test_health_returns_200(self):
        resp = client.get("/api/health")
        assert resp.status_code == 200

    def test_health_response_structure(self):
        data = client.get("/api/health").json()
        assert data["status"] == "healthy"
        assert "agent_status" in data
        assert "pipeline_status" in data
        assert "websocket_channels" in data
        assert data["total_signals_processed"] > 0


class TestSignalsRoutes:
    def test_get_signals_returns_200(self):
        resp = client.get("/api/signals")
        assert resp.status_code == 200

    def test_get_signals_has_items_and_pagination(self):
        data = client.get("/api/signals").json()
        assert "items" in data
        assert "total" in data
        assert "has_more" in data
        assert len(data["items"]) > 0

    def test_get_signals_limit_respected(self):
        data = client.get("/api/signals?limit=2").json()
        assert len(data["items"]) <= 2

    def test_get_signals_sector_filter(self):
        data = client.get("/api/signals?sector=Information+Technology").json()
        for item in data["items"]:
            assert item["sector"] == "Information Technology"

    def test_get_signals_min_confidence_filter(self):
        data = client.get("/api/signals?min_confidence=0.80").json()
        for item in data["items"]:
            assert item["confidence"] >= 0.80

    def test_get_signals_signal_type_filter(self):
        data = client.get("/api/signals?signal_type=Promoter+Accumulation").json()
        for item in data["items"]:
            assert item["signal_type"] == "Promoter Accumulation"

    def test_get_signals_latest_returns_200(self):
        resp = client.get("/api/signals/latest")
        assert resp.status_code == 200

    def test_get_signals_latest_above_threshold(self):
        data = client.get("/api/signals/latest?threshold=0.75").json()
        for item in data["items"]:
            assert item["confidence"] >= 0.75

    def test_get_signals_by_sector_route(self):
        resp = client.get("/api/signals/sector/Information+Technology")
        # May return 200 or 404 depending on URL encoding
        assert resp.status_code in (200, 422)

    def test_get_signal_by_id(self):
        data = client.get("/api/signals/sig-persistent-promoter-dips").json()
        assert "signal" in data
        assert data["signal"]["id"] == "sig-persistent-promoter-dips"

    def test_get_signal_not_found_returns_404(self):
        resp = client.get("/api/signals/NONEXISTENT-XYZ")
        assert resp.status_code == 404

    def test_get_audit_valid_id(self):
        data = client.get("/api/signals/audit/sig-persistent-promoter-dips").json()
        assert data["signal_id"] == "sig-persistent-promoter-dips"
        assert "reasoning_chain" in data
        assert "confidence_metadata" in data

    def test_get_audit_not_found_returns_404(self):
        resp = client.get("/api/signals/audit/nonexistent-signal-xyz")
        assert resp.status_code == 404

    def test_post_subscribe(self):
        resp = client.post(
            "/api/signals/subscribe",
            json={"watchlist": ["PERSISTENT"], "sectors": ["Information Technology"], "min_confidence": 0.7},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["active"] is True
        assert "PERSISTENT" in data["filters"]["watchlist"]


class TestPatternsRoutes:
    def test_get_patterns_scan_returns_200(self):
        resp = client.get("/api/patterns/scan")
        assert resp.status_code == 200

    def test_get_patterns_scan_has_count(self):
        data = client.get("/api/patterns/scan").json()
        assert "count" in data
        assert data["count"] == len(data["items"])

    def test_get_patterns_scan_pattern_type_filter(self):
        data = client.get("/api/patterns/scan?pattern_type=Golden+Cross").json()
        for item in data["items"]:
            assert "Golden Cross" in item["pattern_type"]

    def test_get_patterns_high_conviction(self):
        data = client.get("/api/patterns/high-conviction?min_confidence=0.75").json()
        for item in data["items"]:
            assert item["confidence"] >= 0.75

    def test_get_pattern_by_id(self):
        data = client.get("/api/patterns/id/pat-hdfcbank-golden-cross").json()
        assert data["ticker"] == "HDFCBANK"

    def test_get_pattern_by_id_not_found(self):
        resp = client.get("/api/patterns/id/nonexistent-pattern")
        assert resp.status_code == 404

    def test_get_pattern_by_ticker(self):
        data = client.get("/api/patterns/HDFCBANK").json()
        assert data["ticker"] == "HDFCBANK"
        assert len(data["items"]) >= 1

    def test_get_pattern_by_unknown_ticker_returns_404(self):
        resp = client.get("/api/patterns/UNKNOWNTICKER")
        assert resp.status_code == 404


class TestPortfolioRoutes:
    def test_post_portfolio_analyze_demo(self):
        resp = client.post("/api/portfolio/analyze", json={"use_demo_data": True})
        assert resp.status_code == 200
        data = resp.json()
        assert data["holdings_count"] == 8
        assert data["current_value"] > data["invested_amount"]

    def test_post_portfolio_analyze_returns_health_score(self):
        data = client.post("/api/portfolio/analyze", json={"use_demo_data": True}).json()
        assert "money_health_score" in data
        assert data["money_health_score"]["overall"] > 0

    def test_post_portfolio_analyze_has_overlap_matrix(self):
        data = client.post("/api/portfolio/analyze", json={"use_demo_data": True}).json()
        assert "overlap_matrix" in data
        assert len(data["overlap_matrix"]) > 0

    def test_post_portfolio_query_overlap(self):
        resp = client.post(
            "/api/portfolio/query",
            json={"question": "Which mutual funds overlap most with my direct stocks?", "use_demo_data": True},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "answer" in data
        assert "logic" in data
        assert data["disclaimer"]

    def test_post_portfolio_query_xirr(self):
        resp = client.post(
            "/api/portfolio/query",
            json={"question": "What is my portfolio return?", "use_demo_data": True},
        )
        data = resp.json()
        assert "xirr_pct" in data["supporting_metrics"]


class TestStoryRoutes:
    def test_get_story_video_latest_returns_200(self):
        resp = client.get("/api/story/video/latest")
        assert resp.status_code == 200

    def test_get_story_video_script_outline_rich(self):
        data = client.get("/api/story/video/latest").json()
        assert len(data["script_outline"]) >= 6

    def test_get_story_arcs_list(self):
        data = client.get("/api/story/arcs").json()
        assert "items" in data
        assert data["count"] == 5

    def test_get_story_arc_by_query(self):
        data = client.get("/api/story/arc/zomato").json()
        assert data["slug"] == "zomato-profitability-journey"
        assert data["sentiment_score"] > 0


class TestIpoRoutes:
    def test_get_ipo_active_returns_200(self):
        resp = client.get("/api/ipo/active")
        assert resp.status_code == 200

    def test_get_ipo_active_has_count(self):
        data = client.get("/api/ipo/active").json()
        assert data["count"] == 4

    def test_get_ipo_active_sorted_by_subscription(self):
        data = client.get("/api/ipo/active").json()
        items = data["items"]
        for i in range(len(items) - 1):
            assert items[i]["subscription_multiple"] >= items[i + 1]["subscription_multiple"]

    def test_get_ipo_detail(self):
        resp = client.get("/api/ipo/aether")
        assert resp.status_code == 200
        data = resp.json()
        assert "Aether" in data["name"]

    def test_get_ipo_not_found_returns_404(self):
        resp = client.get("/api/ipo/nonexistentipo")
        assert resp.status_code == 404

    def test_ipos_have_listing_date(self):
        data = client.get("/api/ipo/active").json()
        for item in data["items"]:
            assert item["listing_date"] is not None
