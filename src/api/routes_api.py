"""REST: upload + offline analyze, saves report JSON."""
import tempfile
from pathlib import Path
from fastapi import APIRouter, UploadFile, File
from src.parsers.pdf_parser import parse_pdf
from src.parsers.html_parser import parse_html
from src.parsers.docx_parser import parse_docx
from src.parsers.pptx_parser import parse_pptx
from src.agents.structure import check_structure
from src.agents.slides import check_slides
from src.agents.q1_reviewer import check_q1
from src.agents.word_choice import check_words
from src.agents.ethics import check_ethics
from src.agents.refs_checker import check_refs
from src.agents.academic import check_academic
from src.agents.consistency import check_consistency
from src.agents.reporter import build_report, build_compare
from src.storage.database import save_report, list_reports, load_report, save_upload, list_docs, mark_doc, delete_doc, resolve_report

router = APIRouter()


def _save_tmp_raw(raw: bytes, filename: str) -> str:
    suffix = Path(filename or "file").suffix
    fd, tmp = tempfile.mkstemp(suffix=suffix)
    with open(tmp, "wb") as f:
        f.write(raw)
    return tmp


@router.post("/api/analyze")
def analyze(thesis: UploadFile = File(None), deck: UploadFile = File(None)):
    thesis_text, headings = "", []
    doc_id = None
    if thesis is not None:
        raw = thesis.file.read()
        entry = save_upload(thesis.filename or "thesis", raw)
        doc_id = entry["id"]
        tmp = _save_tmp_raw(raw, thesis.filename or "file")
        name = (thesis.filename or "").lower()
        if name.endswith(".pdf"):
            r = parse_pdf(tmp)
            thesis_text = r.get("text", "")
        elif name.endswith(".html") or name.endswith(".htm"):
            r = parse_html(tmp)
            thesis_text = r.get("text", "")
            headings = r.get("headings", [])
        elif name.endswith(".docx"):
            r = parse_docx(tmp)
            thesis_text = r.get("text", "")
    slide_items, slide_text = [], ""
    deck_id = None
    if deck is not None:
        draw = deck.file.read()
        dentry = save_upload(deck.filename or "deck", draw)
        deck_id = dentry["id"]
        tmp = _save_tmp_raw(draw, deck.filename or "file")
        r = parse_pptx(tmp)
        slide_items = r.get("items", [])
        slide_text = " ".join(" ".join(s.get("bullets", [])) for s in slide_items)
    parts = [
        check_structure(thesis_text, headings),
        check_q1(thesis_text, headings),
        check_words(thesis_text),
        check_ethics(thesis_text),
        check_refs(thesis_text),
        check_academic(thesis_text),
    ]
    if slide_items:
        parts.append(check_slides(slide_items))
        parts.append(check_consistency(thesis_text, slide_text))
    report = build_report(parts)
    rid = save_report(report)
    status = "Analyzed" if report.get("verdict") == "Pass" else ("Needs review" if report.get("major", 0) > 0 else "Analyzed")
    if doc_id:
        mark_doc(doc_id, status, rid)
    if deck_id:
        mark_doc(deck_id, status, rid)
    return {"id": rid, "doc": doc_id, "deck": deck_id, **report}


@router.get("/api/docs")
def docs():
    return {"docs": list_docs()}


@router.delete("/api/docs/{doc_id}")
def remove_doc(doc_id: str):
    ok = delete_doc(doc_id)
    if not ok:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="doc not found")
    return {"ok": True, "id": doc_id}


@router.get("/health")
def health():
    return {"ok": True}


@router.get("/api/history")
def history():
    return {"reports": list_reports()}


@router.get("/api/report/{rid}")
def report(rid: str):
    return load_report(rid)


@router.get("/api/compare")
def compare(a: str = "", b: str = ""):
    """Compare two library docs (or reports): version progress or mine-vs-journal."""
    from fastapi import HTTPException
    if not (a or "").strip() or not (b or "").strip():
        raise HTTPException(status_code=400, detail="query params a and b required")
    da, ra = resolve_report(a)
    db, rb = resolve_report(b)
    if ra is None:
        raise HTTPException(status_code=404, detail=f"no analyzed report for '{a}'")
    if rb is None:
        raise HTTPException(status_code=404, detail=f"no analyzed report for '{b}'")

    def summ(d, r, ref):
        return {
            "id": (d or {}).get("id") or r.get("id") or ref,
            "name": (d or {}).get("name") or r.get("id") or ref,
            "report": r.get("id"),
            "overall": r.get("overall", 0),
            "verdict": r.get("verdict", "-"),
            "major": r.get("major", 0),
            "minor": r.get("minor", 0),
        }

    return {"a": summ(da, ra, a), "b": summ(db, rb, b), "delta": build_compare(ra, rb)}


@router.get("/api/verify-doi")
def verify_doi(doi: str):
    doi = (doi or "").strip()
    if not doi:
        return {"ok": False, "error": "doi required"}
    try:
        import httpx

        url = f"https://api.crossref.org/works/{doi}"
        r = httpx.get(url, timeout=20, headers={"User-Agent": "Oggy-Organizer/1.0"})
        if r.status_code != 200:
            return {"ok": False, "doi": doi, "found": False, "status": r.status_code}
        j = r.json().get("message", {})
        return {
            "ok": True,
            "doi": doi,
            "found": True,
            "title": (j.get("title") or [""])[0][:200],
            "year": (j.get("published-print") or j.get("published-online") or {}).get("date-parts", [[None]])[0][0],
        }
    except Exception as e:
        return {"ok": False, "doi": doi, "error": str(e)}
