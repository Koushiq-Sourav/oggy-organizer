def test_build_compare_delta():
    from src.agents.reporter import build_compare
    a = {
        "overall": 56, "verdict": "Fix", "major": 5, "minor": 3,
        "parts": [{"agent": "q1", "score": 50}, {"agent": "ethics", "score": 60}],
        "fix_list": ["[q1] missing gap", "[ethics] missing declaration"],
    }
    b = {
        "overall": 97, "verdict": "Pass", "major": 0, "minor": 1,
        "parts": [{"agent": "q1", "score": 90}, {"agent": "ethics", "score": 100}],
        "fix_list": ["[ethics] missing declaration", "[words] weak word x2"],
    }
    d = build_compare(a, b)
    assert d["score_delta"] == 41
    assert d["major_delta"] == -5
    assert d["fixed"] == ["[q1] missing gap"]
    assert d["remaining"] == ["[ethics] missing declaration"]
    assert d["new"] == ["[words] weak word x2"]
    agents = {r["agent"]: r for r in d["agents"]}
    assert agents["q1"]["delta"] == 40


def test_build_compare_empty():
    from src.agents.reporter import build_compare
    d = build_compare({}, {})
    assert d["score_delta"] == 0
    assert d["fixed"] == [] and d["new"] == []
