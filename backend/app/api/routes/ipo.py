from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.services.ipo import get_ipo_by_name, list_active_ipos


router = APIRouter(prefix="/ipo", tags=["ipo"])


@router.get("/active")
async def ipo_active() -> dict:
    ipos = await list_active_ipos()
    return {"items": [ipo.model_dump() if hasattr(ipo, "model_dump") else ipo for ipo in ipos], "count": len(ipos)}


@router.get("/{name}")
async def ipo_detail(name: str) -> dict:
    try:
        ipo = await get_ipo_by_name(name)
        return ipo.model_dump() if hasattr(ipo, "model_dump") else ipo
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"IPO not found: {name}") from exc
