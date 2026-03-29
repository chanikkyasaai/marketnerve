from __future__ import annotations

from fastapi import APIRouter

from app.services.story import get_latest_video, get_story_arc, list_all_arcs, trigger_video_generation


router = APIRouter(prefix="/story", tags=["story"])


@router.get("/video/latest")
async def story_video_latest() -> dict:
    video = await get_latest_video()
    return video.model_dump()


@router.post("/video/generate")
async def story_video_generate() -> dict:
    return await trigger_video_generation()


@router.get("/arcs")
async def story_arcs_list() -> dict:
    arcs = await list_all_arcs()
    return {"items": [arc.model_dump() for arc in arcs], "count": len(arcs)}


@router.get("/arc/{query}")
async def story_arc(query: str) -> dict:
    arc = await get_story_arc(query)
    return arc.model_dump()
