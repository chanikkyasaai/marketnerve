from __future__ import annotations

from fastapi import APIRouter

from app.services.health import get_health


router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    return get_health().model_dump()
