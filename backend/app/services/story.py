from __future__ import annotations

from app.data.repository import repository
from app.models.schemas import LiveEvent, StoryArc, StoryEvent, StoryVideo


_SENTIMENT_SCORES: dict[str, float] = {
    "constructive": 0.7,
    "bullish": 0.85,
    "cautiously-positive": 0.6,
    "neutral": 0.5,
    "high-activity": 0.65,
    "bearish": 0.2,
}


def get_latest_video() -> StoryVideo:
    raw = repository.get_stories()["daily_video"]
    return StoryVideo(
        **raw,
        formats=["1080x1920", "1920x1080", "1280x720"],
        lead_signal_id="sig-persistent-promoter-dips",
        script_outline=[
            "Nifty close and index tone — breadth analysis",
            "Top gainers and losers snapshot with sector attribution",
            "Institutional flows summary — FII vs DII tally",
            "Lead AI signal of the day — Persistent Systems promoter accumulation",
            "Pattern of the day — HDFCBANK Golden Cross setup",
            "IPO and primary market briefing",
        ],
    )


def _arc_to_model(arc: dict) -> StoryArc:
    sentiment = arc.get("sentiment", "neutral")
    return StoryArc(
        slug=arc["slug"],
        title=arc["title"],
        thesis=arc["thesis"],
        sentiment=sentiment,
        sentiment_score=_SENTIMENT_SCORES.get(sentiment, 0.5),
        what_to_watch_next=_what_to_watch(arc["slug"]),
        events=[StoryEvent(**event) for event in arc["events"]],
    )


def _what_to_watch(slug: str) -> list[str]:
    defaults = {
        "zomato-profitability-journey": [
            "Quick-commerce margin exit rate",
            "Blinkit order frequency growth",
            "Competitive discount intensity from Swiggy Instamart",
        ],
        "hdfc-merger-integration": [
            "NIM trajectory over next 2 quarters",
            "CASA ratio recovery timeline",
            "RBI liquidity stance and its impact on cost of funds",
        ],
        "adani-group-recovery": [
            "US DOJ superseding indictment outcome",
            "FII re-entry pace into Adani listed entities",
            "Debt reduction milestones from group treasury",
        ],
        "nifty-it-fii-rotation": [
            "US discretionary IT spending cues from CIO surveys",
            "INR/USD rate trajectory",
            "TCS and Infosys management guidance tone",
        ],
        "india-ofs-ipo-surge-2026": [
            "SEBI approval pipeline",
            "Retail subscription patterns in Tier 2/3 cities",
            "GMP compression risk ahead of listing",
        ],
    }
    return defaults.get(slug, ["Near-term operating metrics", "Consensus expectation changes"])


def get_story_arc(query: str) -> StoryArc:
    arcs = repository.get_stories()["arcs"]
    normalized = query.lower().replace(" ", "-")
    for arc in arcs:
        if normalized in arc["slug"] or query.lower() in arc["title"].lower():
            return _arc_to_model(arc)
    return _arc_to_model(arcs[0])


def list_all_arcs() -> list[StoryArc]:
    return [_arc_to_model(arc) for arc in repository.get_stories()["arcs"]]


def get_live_filing_events() -> list[LiveEvent]:
    return [
        LiveEvent(
            channel="filings",
            event_type="filing_classified",
            generated_at=repository.generated_at(),
            payload={
                "ticker": signal["ticker"],
                "filing_type": signal["signal_type"],
                "source_names": signal["sources"],
                "confidence": signal["confidence"],
                "summary": signal["summary"][:100],
            },
        )
        for signal in repository.get_signals()
    ]
