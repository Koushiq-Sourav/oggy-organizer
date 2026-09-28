"""Memory of the app: plain JSON files, no database server.
docs.json lists files, reports/ keeps verdicts, uploads/ keeps raws.
IDs carry microseconds so two fast uploads never clash.
Cloud note: read-only hosts (Vercel) fall back to /tmp automatically."""
import json
from pathlib import Path
from datetime import datetime


def _writable_data_dir() -> Path:
    """Bundled data/ locally, /tmp on read-only cloud disks."""
    bundled = Path(__file__).resolve().parents[2] / "data"
    try:
        bundled.mkdir(parents=True, exist_ok=True)
        probe = bundled / ".write_test"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        return bundled
    except Exception:
        fallback = Path("/tmp/oggy-data")
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback


DATA_DIR = _writable_data_dir()
ROOT = DATA_DIR / "reports"
ROOT.mkdir(parents=True, exist_ok=True)
UPLOADS = DATA_DIR / "uploads"
UPLOADS.mkdir(parents=True, exist_ok=True)
DOCS = DATA_DIR / "docs.json"

KIND_BY_EXT = {
    ".pdf": "papers", ".html": "papers", ".htm": "papers", ".docx": "papers",
    ".pptx": "slides",
    ".md": "notes", ".txt": "notes",
    ".csv": "data", ".xlsx": "data", ".xls": "data",
}


def kind_for(name: str) -> str:
    """File extension to library shelf."""
    return KIND_BY_EXT.get(Path(name or "").suffix.lower(), "papers")


def save_upload(filename: str, data: bytes) -> dict:
    """Store file bytes, prepend its doc entry."""
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    safe = Path(filename or "file").name
    stored = f"{stamp}_{safe}"
    (UPLOADS / stored).write_bytes(data)
    docs = list_docs()
    ext = Path(filename or "file").suffix.upper().lstrip(".") or "File"
    entry = {"id": stored, "name": safe, "kind": kind_for(safe), "detail": ext + " document", "status": "Queued", "report": None}
    docs.insert(0, entry)
    DOCS.write_text(json.dumps(docs[:200], indent=2), encoding="utf-8")
    return entry


def list_docs() -> list:
    """Read the doc index (empty list if none)."""
    if not DOCS.exists():
        return []
    try:
        return json.loads(DOCS.read_text(encoding="utf-8"))
    except Exception:
        return []


def mark_doc(doc_id: str, status: str, report: str | None = None) -> None:
    """Stamp status plus report onto one doc."""
    docs = list_docs()
    for d in docs:
        if d.get("id") == doc_id:
            d["status"] = status
            if report:
                d["report"] = report
    DOCS.write_text(json.dumps(docs[:200], indent=2), encoding="utf-8")


def delete_doc(doc_id: str) -> bool:
    """Remove a doc from docs.json + delete its uploaded file. Reports kept."""
    docs = list_docs()
    kept = [d for d in docs if d.get("id") != doc_id]
    if len(kept) == len(docs):
        return False
    DOCS.write_text(json.dumps(kept[:200], indent=2), encoding="utf-8")
    try:
        target = (UPLOADS / Path(doc_id).name)
        if target.exists() and target.is_file():
            target.unlink()
    except Exception:
        pass
    return True


def save_report(report: dict) -> str:
    """Store report JSON under a microsecond id."""
    name = datetime.now().strftime("%Y%m%d-%H%M%S-%f") + ".json"
    payload = {"id": name, **report}
    (ROOT / name).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return name


def list_reports() -> list:
    """Newest 20 report summaries."""
    out = []
    for p in sorted(ROOT.glob("*.json"), reverse=True)[:20]:
        try:
            j = json.loads(p.read_text(encoding="utf-8"))
            out.append(
                {
                    "id": p.name,
                    "overall": j.get("overall", 0),
                    "verdict": j.get("verdict", "-"),
                    "major": j.get("major", 0),
                    "minor": j.get("minor", 0),
                }
            )
        except Exception:
            continue
    return out


def load_report(rid: str) -> dict:
    """One report, or a missing/error placeholder."""
    p = ROOT / Path(rid).name
    if not p.exists():
        return {"overall": 0, "verdict": "missing", "major": 0, "minor": 0, "parts": [], "fix_list": [f"Report {rid} not found"]}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        return {"overall": 0, "verdict": "error", "major": 0, "minor": 0, "parts": [], "fix_list": [str(e)]}


def resolve_report(ref: str):
    """Accept a doc id or a report id. Returns (doc|None, report|None)."""
    ref = (ref or "").strip()
    if not ref:
        return None, None
    for d in list_docs():
        if d.get("id") == ref:
            rid = d.get("report")
            if not rid:
                return d, None
            rep = load_report(rid)
            if rep.get("verdict") in ("missing", "error"):
                return d, None
            return d, {"id": rid, **rep}
    rep = load_report(ref)
    if rep.get("verdict") in ("missing", "error"):
        return None, None
    return None, {"id": Path(ref).name, **rep}
