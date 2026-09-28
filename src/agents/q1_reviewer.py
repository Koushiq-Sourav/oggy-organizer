"""Q1 reviewer simulation: editor desk check + novelty + rigor, offline first."""
from typing import Dict, Any, List
from src.utils.scoring import score_from_issues, verdict

WEAK_NOVELTY_PHRASES = ["in this paper we", "we propose", "we present"]


def check_q1(text: str, headings: List[str] | None = None) -> Dict[str, Any]:
    low = (text or "").lower()
    issues: List[str] = []
    major = 0
    minor = 0
    if "gap" not in low and "research gap" not in low:
        major += 1
        issues.append("No explicit research gap sentence found (Q1 desk risk)")
    if "limitation" not in low:
        minor += 1
        issues.append("No limitations section found (reviewers expect it)")
    if "method" not in low:
        major += 1
        issues.append("Methods not detected (reproducibility fail)")
    if "result" not in low and "discussion" not in low:
        major += 1
        issues.append("Results/discussion not detected")
    if "novel" not in low and "contribution" not in low:
        minor += 1
        issues.append("Contribution/novelty not stated crisply on page 1 style")
    total = 6
    score = score_from_issues(total, major, minor)
    return {
        "agent": "q1_reviewer",
        "score": score,
        "verdict": verdict(score),
        "issues": issues,
        "major": major,
        "minor": minor,
        "triangle": {"novelty": score, "value": score, "impact": max(0, score - 5)},
    }
