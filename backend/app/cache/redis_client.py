"""Upstash Redis client using REST API — no separate library needed."""
import json
import logging
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)

_http: httpx.AsyncClient | None = None

def _client() -> httpx.AsyncClient:
    global _http
    if _http is None or _http.is_closed:
        _http = httpx.AsyncClient(
            base_url=settings.upstash_redis_rest_url,
            headers={"Authorization": f"Bearer {settings.upstash_redis_rest_token}"},
            timeout=8.0,
        )
    return _http

async def cache_get(key: str) -> dict | list | None:
    """Get a JSON value from Redis cache."""
    if not settings.has_redis:
        return None
    try:
        resp = await _client().get(f"/get/{key}")
        data = resp.json()
        if data.get("result") is None:
            return None
        return json.loads(data["result"])
    except Exception as e:
        logger.debug(f"Redis GET {key} failed: {e}")
        return None

async def cache_set(key: str, value: dict | list, ttl_seconds: int = 1800) -> bool:
    """Set a JSON value in Redis cache with TTL."""
    if not settings.has_redis:
        return False
    try:
        payload = json.dumps(value, default=str)
        resp = await _client().post("/", json=["SET", key, payload, "EX", str(ttl_seconds)])
        return resp.json().get("result") == "OK"
    except Exception as e:
        logger.debug(f"Redis SET {key} failed: {e}")
        return False

async def cache_delete(key: str) -> bool:
    """Delete a key from cache."""
    if not settings.has_redis:
        return False
    try:
        await _client().get(f"/del/{key}")
        return True
    except Exception:
        return False

async def cache_get_or_set(key: str, factory, ttl: int = 1800):
    """Get from cache; if miss, call factory() and cache the result."""
    cached = await cache_get(key)
    if cached is not None:
        return cached
    result = await factory()
    if result:
        await cache_set(key, result, ttl)
    return result
