"""Consistency agent: thesis vs slides term overlap, offline TF-IDF-lite."""
import re
from typing import Dict, Any
from src.utils.scoring import score_from_issues, verdict


def check_consistency(thesis_text: str, slide_text: str) -> Dict[str, Any]:
    def toks(s: str):
        return set(re.findall(r"[a-z]{5,}", (s or "").lower()))

    a, b = toks(thesis_text), toks(slide_text)
    if not a or not b:
        return {
            "agent": "consistency",
            "score": 60,
            "verdict": "Fix",
            "issues": ["Thesis or slides text empty, cannot compare"],
            "major": 0,
            "minor": 1,
        }
    overlap = len(a & b) / max(1, len(b))
    issues = []
    minor = 0
    if overlap < 0.25:
        minor += 1
        issues.append(f"Low thesis-slide overlap ({overlap:.0%}), slides may drift off-topic")
    score = score_from_issues(3, 0, minor)
    return {
        "agent": "consistency",
        "score": score,
        "verdict": verdict(score),
        "issues": issues,
        "major": 0,
        "minor": minor,
        "overlap": round(overlap, 3),
    }
