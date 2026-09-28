"""HTML thesis parser for THESIS.html style files."""
from pathlib import Path
from typing import Dict, Any, List
from src.utils.text_clean import clean_text


def parse_html(path: str) -> Dict[str, Any]:
    p = Path(path)
    if not p.exists():
        return {"ok": False, "error": "file not found", "path": path}
    try:
        from bs4 import BeautifulSoup
    except Exception as e:
        return {"ok": False, "error": f"bs4 missing: {e}", "path": path}
    try:
        soup = BeautifulSoup(p.read_text(encoding="utf-8", errors="ignore"), "lxml")
        headings: List[str] = [clean_text(h.get_text()) for h in soup.find_all(["h1", "h2", "h3"])]
        headings = [h for h in headings if h]
        text = clean_text(soup.get_text("\n"))
        return {
            "ok": True,
            "path": str(p),
            "headings": headings,
            "text": text,
            "chars": len(text),
        }
    except Exception as e:
        return {"ok": False, "error": str(e), "path": str(p)}
