"""WS progress channel: clients get staged ticks during long analysis."""
from fastapi import APIRouter, WebSocket

router = APIRouter()


@router.websocket("/ws/progress")
async def progress(ws: WebSocket):
    await ws.accept()
    for pct in (10, 30, 55, 80, 100):
        await ws.send_json({"pct": pct})
    await ws.close()
