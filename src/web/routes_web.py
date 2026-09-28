"""Web pages: dashboard, report view, compare."""
from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from src.storage.database import list_reports, load_report

BASE = Path(__file__).resolve().parents[2]
templates = Jinja2Templates(directory=str(BASE / "templates"))

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    history = list_reports()
    last = history[0] if history else None
    return templates.TemplateResponse(
        request, "pages/dashboard.html", {"history": history, "last": last, "title": "Oggy Organizer"}
    )


@router.get("/upload", response_class=HTMLResponse)
def upload(request: Request):
    # Thesis review page removed — library Add files is the single entry.
    return RedirectResponse(url="/", status_code=302)


@router.get("/report/{rid}", response_class=HTMLResponse)
def report_page(request: Request, rid: str):
    report = load_report(rid)
    return templates.TemplateResponse(
        request, "pages/report.html", {"report": report, "rid": rid, "title": f"Report {rid}"}
    )


@router.get("/compare", response_class=HTMLResponse)
def compare(request: Request):
    return templates.TemplateResponse(request, "pages/compare.html", {"title": "Compare - Oggy Organizer"})
