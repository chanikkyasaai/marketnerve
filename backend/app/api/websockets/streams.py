from __future__ import annotations

from fastapi import APIRouter, WebSocket

from app.services.patterns import get_live_pattern_events
from app.services.signals import get_live_signal_events
from app.services.story import get_live_filing_events


router = APIRouter(tags=["streams"])


@router.websocket("/signals")
async def live_signals(websocket: WebSocket) -> None:
    await websocket.accept()
    for event in get_live_signal_events():
        await websocket.send_json(event.model_dump())
    await websocket.close()


@router.websocket("/patterns")
async def live_patterns(websocket: WebSocket) -> None:
    await websocket.accept()
    for event in get_live_pattern_events():
        await websocket.send_json(event.model_dump())
    await websocket.close()


@router.websocket("/filings")
async def live_filings(websocket: WebSocket) -> None:
    await websocket.accept()
    for event in get_live_filing_events():
        await websocket.send_json(event.model_dump())
    await websocket.close()
