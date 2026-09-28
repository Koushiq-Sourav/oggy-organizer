"""DOCX thesis draft parser."""
from pathlib import Path
from typing import Dict, Any
from src.utils.text_clean import clean_text


def parse_docx(path: str) -> Dict[str, Any]:
    p = Path(path)
    if not p.exists():
        return {"ok": False, "error": "file not found", "path": path}
    try:
        import docx
    except Exception as e:
        return {"ok": False, "error": f"python-docx missing: {e}", "path": path}
    try:
        doc = docx.Document(str(p))
        paras = [clean_text(pg.text) for pg in doc.paragraphs]
        paras = [t for t in paras if t]
        full = "\n\n".join(paras)
        return {
            "ok": True,
            "path": str(p),
            "paragraphs": len(paras),
            "text": full,
            "chars": len(full),
        }
    except Exception as e:
        return {"ok": False, "error": str(e), "path": str(p)}
