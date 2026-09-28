"""Academic agent: methods depth, results-discussion link, citations breadth."""
from typing import Dict, Any, List
from src.utils.scoring import score_from_issues, verdict


def check_academic(text: str) -> Dict[str, Any]:
    low = (text or "").lower()
    issues: List[str] = []
    major = 0
    minor = 0
    if "assumption" not in low and "validation" not in low:
        minor += 1
        issues.append("Methods lack assumptions/validation wording")
    if low.count("figure") + low.count("table") < 3:
        minor += 1
        issues.append("Few figure/table mentions (<3), Q1 expects clear evidence")
    if "et al" not in low and "doi" not in low:
        minor += 1
        issues.append("Citation signals weak (no et al/DOI pattern found)")
    total = 5
    score = score_from_issues(total, major, minor)
    return {
        "agent": "academic",
        "score": score,
        "verdict": verdict(score),
        "issues": issues,
        "major": major,
        "minor": minor,
    }
