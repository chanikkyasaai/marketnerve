from __future__ import annotations

from fastapi import APIRouter

from app.services.health import get_health


router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict:
    h = await get_health()
    return h.model_dump() if hasattr(h, "model_dump") else h
