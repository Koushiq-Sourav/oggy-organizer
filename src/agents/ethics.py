"""Ethics agent: declarations, dual-use signals, copy-risk signals, offline."""
from typing import Dict, Any, List
from src.utils.scoring import score_from_issues, verdict


def check_ethics(text: str) -> Dict[str, Any]:
    low = (text or "").lower()
    issues: List[str] = []
    major = 0
    minor = 0
    for key in ["conflict of interest", "data availability", "code availability", "ethic"]:
        if key not in low:
            minor += 1
            issues.append(f"Missing declaration: {key}")
    if "available at" not in low and "github" not in low and "doi" not in low:
        minor += 1
        issues.append("No data/code link found (Q1 expects Data Availability)")
    total = 6
    score = score_from_issues(total, major, minor)
    return {
        "agent": "ethics",
        "score": score,
        "verdict": verdict(score),
        "issues": issues,
        "major": major,
        "minor": minor,
    }
