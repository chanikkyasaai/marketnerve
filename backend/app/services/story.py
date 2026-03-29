"""
Story Engine — live Gemini-powered story arc generation.
Arcs are generated from live signals + Gemini knowledge, cached for 2h.
"""
from __future__ import annotations
import asyncio
import logging
from datetime import datetime, timezone

from app.data.repository import repository
from app.ai.gemini_client import gemini_json
from app.models.schemas import StoryArc, StoryEvent, StoryVideo
from app.data.nse_fetcher import fetch_fii_dii

logger = logging.getLogger(__name__)

_video_job_state: dict = {
    "state": "idle",
    "progress_pct": 0,
    "estimated_seconds_remaining": 0,
    "outputs": ["1080x1920", "1920x1080", "1280x720"],
    "updated_at": None,
}
_video_job_task: asyncio.Task | None = None

_SENTIMENT_SCORES: dict[str, float] = {
    "constructive":          0.70,
    "bullish":               0.85,
    "cautiously-positive":   0.60,
    "neutral":               0.50,
    "high-activity":         0.65,
    "bearish":               0.20,
}

# Five major ongoing story themes — AI generates fresh narratives each time
STORY_THEMES = [
    {
        "slug": "zomato-profitability-journey",
        "theme": "Zomato's path to sustainable profitability: Blinkit growth, quick commerce margins, and competitive dynamics with Swiggy Instamart.",
        "ticker": "ZOMATO",
        "sector": "Consumer Internet",
    },
    {
        "slug": "hdfc-merger-integration",
        "theme": "HDFC Bank post-merger integration: NIM compression, CASA ratio recovery, and balance sheet normalization after India's largest bank merger.",
        "ticker": "HDFCBANK",
        "sector": "Financial Services",
    },
    {
        "slug": "adani-group-recovery",
        "theme": "Adani Group's rebound after the Hindenburg report: debt reduction, FII return, and resumption of capex across ports, green energy and airports.",
        "ticker": "ADANIENT",
        "sector": "Conglomerate",
    },
    {
        "slug": "nifty-it-fii-rotation",
        "theme": "Nifty IT sector FII rotation: US tech spending outlook, INR/USD dynamics, and whether TCS/Infosys will lead or lag a global tech rally.",
        "ticker": "TCS",
        "sector": "Information Technology",
    },
    {
        "slug": "india-ofs-ipo-surge-2026",
        "theme": "India's 2026 IPO and OFS boom: SEBI pipeline, retail subscription trends, GMP dynamics and which upcoming listings deserve attention.",
        "ticker": "NSEI",
        "sector": "Primary Markets",
    },
]

STORY_ARC_PROMPT = """You are MarketNerve Story Engine — an expert Indian equity market journalist.

Generate a concise, intelligent story arc about the following ongoing theme.
Use your knowledge of Indian markets up to your training cutoff.
The tone should be analytical, like a Bloomberg or ET Markets deep-dive.

Story Theme: {theme}
Ticker: {ticker}
Sector: {sector}
Current Date Context: {date}

Additional Market Context (from live signals pipeline):
{signals_context}

Generate a story arc. Return JSON exactly matching:
{{
  "title": "compelling 6-10 word headline about this arc",
  "thesis": "2-3 sentences: the key narrative, what's happening and why it matters to investors",
  "sentiment": "one of: bullish | constructive | cautiously-positive | neutral | high-activity | bearish",
  "events": [
    {{"date": "YYYY-MM-DD or 'Q4 2024' format", "label": "event name", "source": "ET Markets | NSE | SEBI | Analyst Report"}},
    {{"date": "...", "label": "...", "source": "..."}},
    {{"date": "...", "label": "...", "source": "..."}}
  ],
  "what_to_watch_next": [
    "specific metric or event to watch (1 sentence)",
    "another specific watchpoint (1 sentence)",
    "third watchpoint (1 sentence)"
  ]
}}

Events should be real, recent (last 6-12 months). Include 3-4 key events."""


async def _generate_arc(theme_config: dict, signals_context: str) -> dict | None:
    prompt = STORY_ARC_PROMPT.format(
        theme=theme_config["theme"],
        ticker=theme_config["ticker"],
        sector=theme_config["sector"],
        date=datetime.now(timezone.utc).strftime("%B %Y"),
        signals_context=signals_context,
    )
    result = await gemini_json(prompt, fallback=None)
    if result and "title" in result:
        result["slug"] = theme_config["slug"]
        return result
    return None


async def _build_signals_context() -> str:
    """Get top signals for Gemini context."""
    try:
        signals = await repository.get_signals()
        if not signals:
            return "No live signals available."
        lines = [
            f"• {s.get('company', '')} ({s.get('ticker', '')}): {s.get('headline', '')} — confidence {round(s.get('confidence', 0)*100)}%"
            for s in signals[:4]
        ]
        return "\n".join(lines)
    except Exception:
        return "Signal context unavailable."


def _arc_to_model(arc: dict) -> StoryArc:
    sentiment = arc.get("sentiment", "neutral")
    raw_watch = arc.get("what_to_watch_next", [])
    if isinstance(raw_watch, str):
        watch_items = [raw_watch]
    elif isinstance(raw_watch, dict):
        watch_items = [str(v).strip() for v in raw_watch.values() if str(v).strip()]
    elif isinstance(raw_watch, list):
        watch_items = [str(v).strip() for v in raw_watch if str(v).strip()]
    else:
        watch_items = []

    raw_events = arc.get("events", [])
    if isinstance(raw_events, dict):
        raw_events = list(raw_events.values())
    if not isinstance(raw_events, list):
        raw_events = []

    events = [
        StoryEvent(
            date=e.get("date", "") if isinstance(e, dict) else "",
            label=e.get("label", "") if isinstance(e, dict) else "",
            source=e.get("source", "") if isinstance(e, dict) else "",
        )
        for e in raw_events[:4]
    ]

    if not watch_items:
        watch_items = [
            "Track next key filing and management guidance updates",
            "Watch volume and institutional flow confirmation",
        ]

    return StoryArc(
        slug=arc["slug"],
        title=arc["title"],
        thesis=arc["thesis"],
        sentiment=sentiment,
        sentiment_score=_SENTIMENT_SCORES.get(sentiment, 0.5),
        what_to_watch_next=watch_items[:3],
        events=events,
    )


async def list_all_arcs() -> list[StoryArc]:
    # 1. Check Redis cache first
    stories = await repository.get_stories()
    cached_arcs = stories.get("arcs", [])
    if cached_arcs:
        logger.debug(f"Story arcs: Redis hit ({len(cached_arcs)} arcs)")
        return [_arc_to_model(a) for a in cached_arcs]

    # 2. Generate live with Gemini
    logger.info("Story arcs: generating live with Gemini...")
    signals_context = await _build_signals_context()
    generated = []
    for theme in STORY_THEMES:
        try:
            arc = await _generate_arc(theme, signals_context)
            if arc:
                generated.append(arc)
                logger.debug(f"Generated arc: {arc['title'][:40]}")
        except Exception as e:
            logger.warning(f"Arc generation failed for {theme['slug']}: {e}")
            # Add a minimal fallback arc for this theme
            generated.append(_minimal_fallback_arc(theme))

    if not generated:
        # Last resort: return seed arcs so app is never empty
        seed = await repository.get_stories_seed_fallback()
        return [_arc_to_model(a) for a in seed.get("arcs", [])]

    # 3. Cache for 2 hours
    await repository.set_stories(generated, ttl=7200)
    return [_arc_to_model(a) for a in generated]


def _minimal_fallback_arc(theme: dict) -> dict:
    """Minimal arc when Gemini is unavailable."""
    return {
        "slug": theme["slug"],
        "title": f"{theme['ticker']} — {theme['sector']} Watch",
        "thesis": "AI analysis temporarily unavailable. Please check back shortly for the full story arc with live market context.",
        "sentiment": "neutral",
        "events": [
            {"date": datetime.now(timezone.utc).strftime("%Y-%m"), "label": "Live monitoring active", "source": "MarketNerve Pipeline"},
        ],
        "what_to_watch_next": [
            "Live Gemini analysis will resume shortly",
            "Check signal feed for latest developments",
        ],
    }


async def get_story_arc(query: str) -> StoryArc | None:
    arcs = await list_all_arcs()
    normalized = query.lower().replace(" ", "-")
    for arc in arcs:
        if normalized in arc.slug or query.lower() in arc.title.lower():
            return arc
    return arcs[0] if arcs else None


async def get_latest_video() -> StoryVideo:
    from app.services.signals import list_signals
    from app.services.patterns import list_patterns

    top_signals = await list_signals(limit=3)
    top_patterns = await list_patterns(limit=2)

    script = [
        "Nifty close and index tone — breadth analysis",
        "Top gainers and losers with sector attribution",
        "FII vs DII institutional flow summary",
    ] + [f"Signal: {s.headline}" for s in top_signals] + [
        f"Pattern: {p.ticker} {p.pattern_type}" for p in top_patterns
    ] + ["IPO and primary market briefing"]

    scene_plan = []
    elapsed = 0
    for idx, step in enumerate(script[:8]):
        duration = 8 if idx == 0 else 9
        scene_plan.append(
            {
                "scene": idx + 1,
                "title": step,
                "visual": "race-chart" if idx in (0, 1) else "data-overlay",
                "start_second": elapsed,
                "end_second": elapsed + duration,
            }
        )
        elapsed += duration

    render_progress = min(96, 40 + (len(top_signals) * 11) + (len(top_patterns) * 7))
    render_status = dict(_video_job_state)
    if render_status.get("state") in ("idle", None):
        render_status = {
            "state": "ready" if scene_plan else "queued",
            "progress_pct": 100 if scene_plan else render_progress,
            "estimated_seconds_remaining": 0 if scene_plan else max(8, 100 - render_progress),
            "outputs": ["1080x1920", "1920x1080", "1280x720"],
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

    today = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return StoryVideo(
        title="Daily Market Intelligence Wrap",
        published_at=today,
        duration_seconds=90,
        summary="AI-generated daily market briefing covering signals, patterns, and institutional flows.",
        embed_url="",
        mp4_url="",
        formats=["1080x1920", "1920x1080", "1280x720"],
        lead_signal_id=top_signals[0].id if top_signals else "sig-market-wrap",
        script_outline=script,
        render_status=render_status,
        scene_plan=scene_plan,
    )


async def _run_video_generation_job() -> None:
    global _video_job_state
    steps = [
        ("queued", 6),
        ("rendering", 28),
        ("rendering", 54),
        ("rendering", 79),
        ("rendering", 93),
        ("ready", 100),
    ]
    for idx, (state, progress) in enumerate(steps):
        remaining = max(0, (len(steps) - idx - 1) * 6)
        _video_job_state = {
            "state": state,
            "progress_pct": progress,
            "estimated_seconds_remaining": remaining,
            "outputs": ["1080x1920", "1920x1080", "1280x720"],
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        await asyncio.sleep(2 if state == "queued" else 4)


async def trigger_video_generation() -> dict:
    global _video_job_task, _video_job_state
    if _video_job_task and not _video_job_task.done():
        return {
            "status": "already-running",
            "render_status": _video_job_state,
        }

    _video_job_state = {
        "state": "queued",
        "progress_pct": 3,
        "estimated_seconds_remaining": 24,
        "outputs": ["1080x1920", "1920x1080", "1280x720"],
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    _video_job_task = asyncio.create_task(_run_video_generation_job())
    return {
        "status": "started",
        "render_status": _video_job_state,
    }
