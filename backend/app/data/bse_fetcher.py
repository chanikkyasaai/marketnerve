"""
BSE India public API fetcher — no API key required.
Fetches corporate filings, SAST disclosures, and pledging changes.
"""
import asyncio
import logging
from datetime import date, timedelta
import httpx

logger = logging.getLogger(__name__)

_BSE_BASE = "https://api.bseindia.com/BseIndiaAPI/api"
_BSE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://www.bseindia.com",
    "Referer": "https://www.bseindia.com/",
}

async def fetch_bse_announcements() -> list[dict]:
    """Fetch recent BSE corporate announcements."""
    # This endpoint provides SAST disclosures, pledging changes, etc.
    url = f"{_BSE_BASE}/AnnSubCategoryGetData/w"
    params = {
        "index": "Equities",
        "category": "Company Update",
        "subcategory": "All",
        "fromdate": (date.today() - timedelta(days=2)).strftime("%Y%m%d"),
        "todate": date.today().strftime("%Y%m%d"),
    }
    
    async with httpx.AsyncClient(headers=_BSE_HEADERS, timeout=15.0) as client:
        try:
            resp = await client.get(url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                items = data if isinstance(data, list) else data.get("Table", [])
                return [
                    {
                        "ticker": item.get("SYMBOL", ""),
                        "subject": item.get("NEWSSUB", ""),
                        "description": item.get("NEWS_DT", ""),
                        "category": item.get("CATEGORYNAME", ""),
                        "dt": item.get("NEWS_DT", ""),
                    }
                    for item in items[:20]
                ]
        except Exception as e:
            logger.debug(f"BSE API failed: {e}")
    return []

async def fetch_sast_disclosures() -> list[dict]:
    """Fetch SAST (Substantial Acquisition of Shares and Takeovers) from BSE."""
    url = f"{_BSE_BASE}/SASTData/w"
    async with httpx.AsyncClient(headers=_BSE_HEADERS, timeout=15.0) as client:
        try:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                items = data if isinstance(data, list) else data.get("Table", [])
                return [
                    {
                        "ticker": item.get("SYMBOL", ""),
                        "company": item.get("COMPANY_NAME", ""),
                        "acquirer": item.get("ACQUIRER_NAME", ""),
                        "quantity": item.get("QUANTITY", 0),
                        "mode": item.get("MODE_OF_ACQUISITION", ""),
                        "date": item.get("DATE_OF_ACQUISITION", ""),
                    }
                    for item in items[:15]
                ]
        except Exception as e:
            logger.debug(f"BSE SAST failed: {e}")
    return []
