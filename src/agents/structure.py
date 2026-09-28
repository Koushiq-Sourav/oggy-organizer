"""Structure agent: required chapters and desk-rule checks, offline."""
from typing import Dict, Any, List
from src.utils.scoring import score_from_issues, verdict

REQUIRED = [
    "declaration",
    "acknowledgement",
    "abstract",
    "introduction",
    "literature",
    "methodology",
    "implementation",
    "testing",
    "conclusion",
    "reference",
]


def check_structure(text: str, headings: List[str] | None = None) -> Dict[str, Any]:
    low = (text or "").lower()
    heads = " ".join(headings or []).lower()
    blob = low + "\n" + heads
    missing: List[str] = [r for r in REQUIRED if r not in blob]
    major = len(missing)
    minor = 0
    issues: List[str] = [f"Missing section: {m}" for m in missing]
    if len(text or "") < 5000:
        minor += 1
        issues.append("Thesis text unusually short (<5000 chars), check full upload")
    total = len(REQUIRED) + 1
    score = score_from_issues(total, major, minor)
    return {
        "agent": "structure",
        "score": score,
        "verdict": verdict(score),
        "missing": missing,
        "issues": issues,
        "major": major,
        "minor": minor,
    }
