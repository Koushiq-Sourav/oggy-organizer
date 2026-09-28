"""PDF thesis parser: text per page, offline first."""
from pathlib import Path
from typing import Dict, Any, List
from src.utils.text_clean import clean_text


def parse_pdf(path: str) -> Dict[str, Any]:
    p = Path(path)
    if not p.exists():
        return {"ok": False, "error": "file not found", "path": path}
    try:
        import fitz  # PyMuPDF
    except Exception:
        try:
            import fitz  # type: ignore
        except Exception as e:
            return {"ok": False, "error": f"pymupdf missing: {e}", "path": path}
    try:
        import fitz
        doc = fitz.open(str(p))
        pages: List[str] = []
        for i, page in enumerate(doc):
            pages.append(clean_text(page.get_text("text")))
        full = "\n\n--- PAGE %d ---\n\n".join(pages) if False else "\n\n".join(
            f"--- PAGE {i+1} ---\n{t}" for i, t in enumerate(pages)
        )
        return {
            "ok": True,
            "path": str(p),
            "pages": len(pages),
            "text": full,
            "chars": len(full),
        }
    except Exception as e:
        return {"ok": False, "error": str(e), "path": str(p)}
