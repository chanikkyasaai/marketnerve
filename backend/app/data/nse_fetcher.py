"""
NSE India public API scraper — no API key required.
Fetches bulk deals, FII/DII data, and corporate announcements.
"""
import asyncio
import logging
from datetime import date, timedelta
import httpx

logger = logging.getLogger(__name__)

_NSE_BASE = "https://www.nseindia.com"
_NSE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.nseindia.com/",
    "Connection": "keep-alive",
    "Cache-Control": "no-cache",
}

async def _get_nse_session() -> httpx.AsyncClient:
    """Get a session with NSE cookies."""
    client = httpx.AsyncClient(headers=_NSE_HEADERS, timeout=15.0, follow_redirects=True)
    try:
        await client.get(_NSE_BASE)  # Initialize session / get cookies
    except Exception:
        pass
    return client

async def _fetch_nse_json(path: str) -> list | dict | None:
    client = await _get_nse_session()
    try:
        resp = await client.get(f"{_NSE_BASE}/api/{path}")
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        logger.debug(f"NSE API failed for {path}: {e}")
    finally:
        await client.aclose()
    return None

async def fetch_bulk_deals() -> list[dict]:
    """Fetch today's NSE bulk deals."""
    data = await _fetch_nse_json("bulk-deals")
    if not data:
        return []
    deals = data if isinstance(data, list) else data.get("data", [])
    return [
        {
            "ticker": d.get("symbol", ""),
            "client": d.get("clientName", ""),
            "trade_type": d.get("buySell", ""),
            "quantity": d.get("quantityTraded", 0),
            "price": d.get("tradePrice", 0),
            "value_cr": round((float(d.get("quantityTraded", 0)) * float(d.get("tradePrice", 0))) / 10000000, 2)
        }
        for d in deals[:30]
    ]

async def fetch_block_deals() -> list[dict]:
    """Fetch today's NSE block deals."""
    data = await _fetch_nse_json("block-deal")
    if not data:
        return []
    deals = data if isinstance(data, list) else data.get("data", [])
    return [
        {
            "ticker": d.get("symbol", ""),
            "client": d.get("clientName", ""),
            "trade_type": d.get("buySell", ""),
            "quantity": d.get("quantityTraded", 0),
            "price": d.get("tradePrice", 0),
            "value_cr": round((float(d.get("quantityTraded", 0)) * float(d.get("tradePrice", 0))) / 10000000, 2)
        }
        for d in deals[:30]
    ]

async def fetch_live_quote(symbol: str) -> dict:
    """Fetch live quote for a symbol from NSE."""
    # Clean symbol for NSE (remove .NS if present)
    clean_symbol = symbol.replace(".NS", "").upper()
    data = await _fetch_nse_json(f"quote-equity?symbol={clean_symbol}")
    if not data or "priceInfo" not in data:
        return {}
    
    p = data["priceInfo"]
    m = data.get("metadata", {})
    return {
        "ticker": clean_symbol,
        "company": m.get("companyName", ""),
        "last_price": p.get("lastPrice", 0),
        "change": p.get("change", 0),
        "p_change": p.get("pChange", 0),
        "open": p.get("open", 0),
        "high": p.get("intraDayHighLow", {}).get("max", 0),
        "low": p.get("intraDayHighLow", {}).get("min", 0),
        "close": p.get("close", 0),
        "vwap": p.get("vwap", 0),
        "volume": data.get("marketDeptOrderBook", {}).get("tradeInfo", {}).get("totalTradedVolume", 0),
        "value_cr": round(data.get("marketDeptOrderBook", {}).get("tradeInfo", {}).get("totalTradedValue", 0) / 100, 2),
    }

async def fetch_fii_dii() -> dict:
    """Fetch latest FII/DII trading activity."""
    data = await _fetch_nse_json("fiidiiTradeReact")
    if not data:
        return {}
    rows = data if isinstance(data, list) else []
    if rows:
        latest = rows[0]
        return {
            "date": latest.get("date", ""),
            "fii_net": float(latest.get("fiiNet", 0)),
            "dii_net": float(latest.get("diiNet", 0)),
        }
    return {}

async def fetch_corporate_announcements(symbol: str = "") -> list[dict]:
    """Fetch recent BSE/NSE corporate announcements for a symbol."""
    path = f"corporate-announcements?index=equities"
    if symbol:
        path += f"&symbol={symbol}"
    data = await _fetch_nse_json(path)
    if not data:
        return []
    items = data if isinstance(data, list) else data.get("data", [])
    return [
        {
            "ticker": item.get("symbol", ""),
            "subject": item.get("subject", ""),
            "description": item.get("desc", ""),
            "dt": item.get("an_dt", ""),
        }
        for item in items[:10]
    ]

def format_announcements_for_gemini(announcements: list[dict], ticker: str) -> str:
    """Format announcements as text for Gemini prompt."""
    relevant = [a for a in announcements if a.get("ticker", "").upper() == ticker.upper()]
    if not relevant:
        return "No significant recent filings on NSE."
    return "\n".join(
        f"• {a['subject']}: {a['description'][:200]}"
        for a in relevant[:3]
    )
