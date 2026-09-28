"""Reporter: merges agent outputs into one Q1-style verdict."""
from typing import Dict, Any, List
from src.utils.scoring import verdict


def build_compare(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    """Delta between two reports: A (base) vs B (target). Pure, testable."""
    afix = a.get("fix_list", []) or []
    bfix = b.get("fix_list", []) or []
    aset, bset = set(afix), set(bfix)
    agents: Dict[str, Dict[str, Any]] = {}
    for p in a.get("parts", []) or []:
        if isinstance(p, dict) and p.get("agent"):
            agents.setdefault(p["agent"], {})["a"] = p.get("score", 0)
    for p in b.get("parts", []) or []:
        if isinstance(p, dict) and p.get("agent"):
            agents.setdefault(p["agent"], {})["b"] = p.get("score", 0)
    rows = [
        {
            "agent": k,
            "a": v.get("a"),
            "b": v.get("b"),
            "delta": (v["b"] - v["a"]) if v.get("a") is not None and v.get("b") is not None else None,
        }
        for k, v in sorted(agents.items())
    ]
    return {
        "score_delta": (b.get("overall", 0) or 0) - (a.get("overall", 0) or 0),
        "verdict_change": f"{a.get('verdict', '-')} → {b.get('verdict', '-')}",
        "major_delta": (b.get("major", 0) or 0) - (a.get("major", 0) or 0),
        "minor_delta": (b.get("minor", 0) or 0) - (a.get("minor", 0) or 0),
        "fixed": [f for f in afix if f not in bset],
        "remaining": [f for f in bfix if f in aset],
        "new": [f for f in bfix if f not in aset],
        "agents": rows,
    }


def build_report(parts: List[Dict[str, Any]]) -> Dict[str, Any]:
    scores = [p.get("score", 0) for p in parts if isinstance(p, dict)]
    overall = int(sum(scores) / len(scores)) if scores else 0
    issues: List[str] = []
    for p in parts:
        for i in p.get("issues", []):
            issues.append(f"[{p.get('agent')}] {i}")
    major = sum(p.get("major", 0) for p in parts)
    minor = sum(p.get("minor", 0) for p in parts)
    return {
        "app": "Oggy Organizer",
        "overall": overall,
        "verdict": verdict(overall),
        "major": major,
        "minor": minor,
        "parts": parts,
        "fix_list": issues[:50],
    }
