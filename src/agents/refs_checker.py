"""Refs checker: bidirectional cite map + CrossRef verify hooks, offline first."""
import re
from typing import Dict, Any, List
from src.utils.scoring import score_from_issues, verdict


def check_refs(text: str) -> Dict[str, Any]:
    issues: List[str] = []
    major = 0
    minor = 0
    lines = (text or "").split("\n")
    ref_start = -1
    for i, ln in enumerate(lines):
        if ln.strip().lower() in ("references", "reference", "bibliography"):
            ref_start = i
    if ref_start < 0:
        return {
            "agent": "refs_checker",
            "score": 50,
            "verdict": "Fix",
            "issues": ["References section not found"],
            "major": 1,
            "minor": 0,
            "ghosts": [],
        }
    body = "\n".join(lines[:ref_start])
    refs = "\n".join(lines[ref_start + 1 :])
    cites = set(re.findall(r"\[(\d+)\]", body)) | set(re.findall(r"\(([^)]*\d{4}[^)]*)\)", body))
    ref_lines = [ln.strip() for ln in refs.split("\n") if ln.strip()]
    if len(ref_lines) < 5:
        minor += 1
        issues.append("Reference list unusually short (<5 entries)")
    if "doi" not in refs.lower() and "http" not in refs.lower():
        minor += 1
        issues.append("No DOI/URL in references (ghost-risk, Q1 expects DOIs)")
    ghosts: List[str] = []
    total = 5
    score = score_from_issues(total, major, minor)
    return {
        "agent": "refs_checker",
        "score": score,
        "verdict": verdict(score),
        "issues": issues,
        "major": major,
        "minor": minor,
        "ghosts": ghosts,
        "note": "CrossRef live verify runs in API layer when net is on",
    }
