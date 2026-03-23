from __future__ import annotations

from fastapi import APIRouter

from app.services.story import get_latest_video, get_story_arc, list_all_arcs


router = APIRouter(prefix="/story", tags=["story"])


@router.get("/video/latest")
def story_video_latest() -> dict:
    return get_latest_video().model_dump()


@router.get("/arcs")
def story_arcs_list() -> dict:
    arcs = list_all_arcs()
    return {"items": [arc.model_dump() for arc in arcs], "count": len(arcs)}


@router.get("/arc/{query}")
def story_arc(query: str) -> dict:
    return get_story_arc(query).model_dump()
