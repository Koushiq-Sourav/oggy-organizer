"""Deterministic 0-100 scoring shared by agents."""
from typing import List


def score_from_issues(total_checks: int, major: int, minor: int) -> int:
    if total_checks <= 0:
        return 0
    penalty = major * 15 + minor * 4
    raw = 100 - int(100 * (major + minor * 0.3) / max(1, total_checks)) - penalty // 4
    return max(0, min(100, raw))


def verdict(score: int) -> str:
    if score >= 85:
        return "Pass"
    if score >= 60:
        return "Fix"
    return "Reject-risk"
