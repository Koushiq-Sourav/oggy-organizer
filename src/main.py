"""Oggy Organizer FastAPI entrypoint."""
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from src.web.routes_web import router as web_router
from src.api.routes_api import router as api_router
from src.api.ws import router as ws_router

BASE = Path(__file__).resolve().parents[1]
app = FastAPI(title="Oggy Organizer")
app.mount("/static", StaticFiles(directory=str(BASE / "static")), name="static")
app.include_router(web_router)
app.include_router(api_router)
app.include_router(ws_router)


@app.get("/health")
def health():
    return {"ok": True, "app": "oggy-organizer"}
