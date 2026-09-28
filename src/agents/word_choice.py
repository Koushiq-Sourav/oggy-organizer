"""Word choice agent: weak words, absolutes, repetition, consistency."""
import re
from collections import Counter
from typing import Dict, Any, List
from src.utils.scoring import score_from_issues, verdict

WEAK = {
    "very": "omit or use precisely",
    "good": "use effective/robust/significant",
    "bad": "use limited/weak/poor",
    "thing": "name the object",
    "a lot": "quantify",
    "big": "quantify",
    "small": "quantify",
    "nice": "remove",
    "stuff": "remove",
}
ABSOLUTES = ["always", "never", "proves", "100%", "perfect"]


def check_words(text: str) -> Dict[str, Any]:
    low = (text or "").lower()
    issues: List[str] = []
    major = 0
    minor = 0
    for w, fix in WEAK.items():
        c = len(re.findall(r"\b" + re.escape(w) + r"\b", low))
        if c >= 3:
            minor += 1
            issues.append(f"Weak word '{w}' x{c}: {fix}")
    for w in ABSOLUTES:
        if w in low:
            minor += 1
            issues.append(f"Absolute '{w}' needs evidence or soften to suggests/demonstrates")
    words = re.findall(r"[a-z]{4,}", low)
    top = Counter(words).most_common(10)
    for w, c in top:
        if c > 40 and w not in ("with", "from", "that", "this", "have"):
            minor += 1
            issues.append(f"Overused '{w}' x{c}: vary wording")
            break
    if "colour" in low and "color" in low:
        minor += 1
        issues.append("US/UK spelling mixed (colour/color), pick one")
    total = 8
    score = score_from_issues(total, major, minor)
    return {
        "agent": "word_choice",
        "score": score,
        "verdict": verdict(score),
        "issues": issues[:20],
        "major": major,
        "minor": minor,
    }
