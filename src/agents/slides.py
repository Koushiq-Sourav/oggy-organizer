"""Slides agent: Maam Option B rules, bullet load, notes, timing."""
from typing import Dict, Any, List
from src.utils.scoring import score_from_issues, verdict


def check_slides(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    issues: List[str] = []
    major = 0
    minor = 0
    total = max(1, len(items) * 2)
    for s in items:
        n = s.get("n", 0)
        bullets = s.get("bullets", []) or []
        flat = " ".join(bullets)
        words = len(flat.split())
        if len(bullets) > 7:
            major += 1
            issues.append(f"Slide {n}: too many text blocks ({len(bullets)}), keep 5-6 max")
        if words > 120:
            minor += 1
            issues.append(f"Slide {n}: wordy ({words} words), cut to 40-60")
        if not s.get("notes"):
            minor += 1
            issues.append(f"Slide {n}: speaker notes missing")
    if items and len(items) < 10:
        minor += 1
        issues.append("Deck short (<10 slides), Q1/thesis defense usually 15-20")
    if items and len(items) > 30:
        minor += 1
        issues.append("Deck long (>30 slides), timing risk for 15-min talk")
    score = score_from_issues(total, major, minor)
    return {
        "agent": "slides",
        "score": score,
        "verdict": verdict(score),
        "slides": len(items),
        "issues": issues,
        "major": major,
        "minor": minor,
    }
