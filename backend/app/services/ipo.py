"""
IPO Intelligence — live NSE data + Gemini AI analysis.
Fetches active IPOs from NSE, enriches with Gemini plain-English breakdown.
"""
from __future__ import annotations
import logging
from datetime import datetime, timezone

import httpx

from app.data.repository import repository
from app.ai.gemini_client import gemini_json
from app.models.schemas import IpoInsight

logger = logging.getLogger(__name__)

_NSE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.nseindia.com/",
    "Accept-Language": "en-US,en;q=0.9",
}

IPO_ENRICH_PROMPT = """You are MarketNerve IPO Intelligence — an expert on Indian primary markets.

IPO Details:
Company: {name}
Issue Price Range: {price_range}
Issue Size: {issue_size}
Open/Close Dates: {dates}

Write a plain-English IPO breakdown for a retail investor with no accounting background.
Be specific and analytical — mention business model, key risks, valuation, and what to watch.

Return JSON:
{{
  "summary": "2-3 sentences: what the company does, key financials, and one specific risk or opportunity",
  "risk_level": "Aggressive | Balanced | Cautious",
  "demand_label": "Hot demand | Healthy demand | Measured demand | Subdued demand"
}}"""

IPO_GENERATE_PROMPT = """You are MarketNerve IPO Intelligence. Today is {date}.

List the 4-6 most significant IPOs currently active or recently opened on Indian markets (NSE/BSE) in {year}.
Include real companies with actual IPO details from your training data.
Focus on IPOs that are open, recently allotted, or upcoming in the next 30 days.

Return JSON array:
[
  {{
    "name": "Company Name Ltd",
    "gmp": 45,
    "subscription_multiple": 8.5,
    "allotment_probability": 0.12,
    "cutoff_price": 450,
    "listing_date": "YYYY-MM-DD or TBD",
    "price_range": "420-450",
    "issue_size": "₹2,400 Cr",
    "dates": "Mar 15-17, 2026",
    "summary": "2-3 sentence plain-English breakdown for retail investor",
    "risk_level": "Aggressive | Balanced | Cautious",
    "demand_label": "Hot demand | Healthy demand | Measured demand | Subdued demand"
  }}
]

GMP (Grey Market Premium) should be realistic in INR.
subscription_multiple: realistic (1-150x range).
allotment_probability: realistic (0.01-0.90 range).
Only include real, significant IPOs — do NOT make up small unknown companies."""


async def _fetch_nse_ipos() -> list[dict]:
    """Attempt to fetch active IPOs from NSE public API."""
    try:
        async with httpx.AsyncClient(headers=_NSE_HEADERS, timeout=12.0, follow_redirects=True) as client:
            # Initialize NSE session
            await client.get("https://www.nseindia.com")
            resp = await client.get("https://www.nseindia.com/api/ipo-current-allotment")
            if resp.status_code == 200:
                data = resp.json()
                items = data if isinstance(data, list) else data.get("data", [])
                if items:
                    return [
                        {
                            "name": item.get("companyName", item.get("symbol", "Unknown")),
                            "symbol": item.get("symbol", ""),
                            "price_range": item.get("priceRange", "TBD"),
                            "issue_size": item.get("issueSize", "TBD"),
                            "dates": f"{item.get('openDate', '')} – {item.get('closeDate', '')}",
                            "listing_date": item.get("listingDate", "TBD"),
                        }
                        for item in items[:8]
                    ]
    except Exception as e:
        logger.debug(f"NSE IPO API failed: {e}")

    # Try BSE IPO endpoint
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                "https://api.bseindia.com/BseIndiaAPI/api/IPOMain/w",
                headers={
                    "Referer": "https://www.bseindia.com/",
                    "User-Agent": "Mozilla/5.0",
                },
            )
            if resp.status_code == 200:
                data = resp.json()
                items = data if isinstance(data, list) else data.get("Table", [])
                if items:
                    return [
                        {
                            "name": item.get("Issuer_Name", item.get("COMPANY_NAME", "Unknown")),
                            "price_range": item.get("Issue_Price", "TBD"),
                            "issue_size": item.get("Issue_Amount", "TBD"),
                            "dates": f"{item.get('Open_Date', '')} – {item.get('Close_Date', '')}",
                            "listing_date": item.get("Listing_Date", "TBD"),
                        }
                        for item in items[:8]
                    ]
    except Exception as e:
        logger.debug(f"BSE IPO API failed: {e}")

    # 4. Final fallback: seeded demo IPOs (never return empty UI unless seed is empty)
    seed_ipos = repository.get_ipos_seed_fallback()
    return sorted([_to_ipo_insight(i) for i in seed_ipos], key=lambda x: (-x.subscription_multiple, -x.gmp))


def _demand_label(subscription_multiple: float) -> str:
    if subscription_multiple >= 10:
        return "Hot demand"
    if subscription_multiple >= 5:
        return "Healthy demand"
    if subscription_multiple >= 2:
        return "Measured demand"
    return "Subdued demand"


def _risk_level(gmp: int, subscription_multiple: float) -> str:
    if gmp >= 100 and subscription_multiple >= 10:
        return "Aggressive"
    if gmp >= 40 or subscription_multiple >= 5:
        return "Balanced"
    return "Cautious"


def _to_ipo_insight(item: dict | IpoInsight) -> IpoInsight:
    if isinstance(item, IpoInsight):
        return item
    if hasattr(item, "model_dump"):
        item = item.model_dump()
    sub = float(item.get("subscription_multiple", 1.0))
    gmp = int(item.get("gmp", 0))
    return IpoInsight(
        name=item["name"],
        gmp=gmp,
        subscription_multiple=sub,
        allotment_probability=float(item.get("allotment_probability", 0.15)),
        demand_label=item.get("demand_label") or _demand_label(sub),
        risk_level=item.get("risk_level") or _risk_level(gmp, sub),
        summary=item.get("summary", "AI analysis pending."),
        cutoff_price=item.get("cutoff_price"),
        listing_date=item.get("listing_date"),
    )


async def list_active_ipos() -> list[IpoInsight]:
    # 1. Check Redis cache
    cached = await repository.get_ipos()
    if cached:
        logger.debug(f"IPOs: cache hit ({len(cached)} ipos)")
        return sorted(
            [_to_ipo_insight(i) for i in cached],
            key=lambda x: (-x.subscription_multiple, -x.gmp),
        )

    # 2. Try NSE/BSE live feed
    nse_ipos = await _fetch_nse_ipos()
    if nse_ipos:
        logger.info(f"IPOs: got {len(nse_ipos)} from NSE/BSE, enriching with Gemini...")
        enriched = []
        for raw in nse_ipos[:6]:
            raw_item = raw.model_dump() if hasattr(raw, "model_dump") else raw
            raw_name = raw_item.get("name", "Unknown") if isinstance(raw_item, dict) else "Unknown"
            try:
                enrich = await gemini_json(
                    IPO_ENRICH_PROMPT.format(
                        name=raw_name,
                        price_range=raw_item.get("price_range", "TBD") if isinstance(raw_item, dict) else "TBD",
                        issue_size=raw_item.get("issue_size", "TBD") if isinstance(raw_item, dict) else "TBD",
                        dates=raw_item.get("dates", "TBD") if isinstance(raw_item, dict) else "TBD",
                    ),
                    fallback={"summary": f"{raw_name} — IPO details being analyzed.", "risk_level": "Balanced", "demand_label": "Measured demand"},
                )
                base = raw_item if isinstance(raw_item, dict) else {"name": raw_name}
                item = {**base, **(enrich or {})}
                # Add placeholder numeric fields if not from NSE
                item.setdefault("gmp", 0)
                item.setdefault("subscription_multiple", 1.0)
                item.setdefault("allotment_probability", 0.20)
                enriched.append(item)
            except Exception as e:
                logger.debug(f"IPO enrich failed for {raw_name}: {e}")
                base = raw_item if isinstance(raw_item, dict) else {"name": raw_name}
                enriched.append({**base, "gmp": 0, "subscription_multiple": 1.0, "allotment_probability": 0.20})

        if enriched:
            await repository.set_ipos(enriched, ttl=3600)
            return sorted([_to_ipo_insight(i) for i in enriched], key=lambda x: (-x.subscription_multiple, -x.gmp))

    # 3. Gemini generates current IPO intelligence from its training knowledge
    logger.info("IPOs: generating with Gemini knowledge...")
    today = datetime.now(timezone.utc)
    raw_list = await gemini_json(
        IPO_GENERATE_PROMPT.format(
            date=today.strftime("%B %d, %Y"),
            year=today.year,
        ),
        fallback=None,
    )
    if isinstance(raw_list, dict):
        # Some providers wrap arrays in an object payload.
        raw_list = raw_list.get("items") or raw_list.get("ipos") or raw_list.get("data") or []

    if raw_list and isinstance(raw_list, list):
        normalized = [i for i in raw_list if isinstance(i, dict) and i.get("name")]
        if normalized:
            await repository.set_ipos(normalized, ttl=3600)
            return sorted([_to_ipo_insight(i) for i in normalized], key=lambda x: (-x.subscription_multiple, -x.gmp))

    # 4. Final fallback: seed IPOs so endpoint never returns empty unless seed is empty.
    seed_ipos = repository.get_ipos_seed_fallback()
    return sorted([_to_ipo_insight(i) for i in seed_ipos], key=lambda x: (-x.subscription_multiple, -x.gmp))


async def get_ipo_by_name(name: str) -> IpoInsight:
    normalized = name.lower().replace("-", " ").replace("_", " ")
    ipos = await list_active_ipos()
    for ipo in ipos:
        if normalized in ipo.name.lower():
            return ipo
    raise KeyError(name)
