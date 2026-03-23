from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.services.ipo import get_ipo_by_name, list_active_ipos


router = APIRouter(prefix="/ipo", tags=["ipo"])


@router.get("/active")
def ipo_active() -> dict:
    ipos = list_active_ipos()
    return {"items": [ipo.model_dump() for ipo in ipos], "count": len(ipos)}


@router.get("/{name}")
def ipo_detail(name: str) -> dict:
    try:
        return get_ipo_by_name(name).model_dump()
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"IPO not found: {name}") from exc
