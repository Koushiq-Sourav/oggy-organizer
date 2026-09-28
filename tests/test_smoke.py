def test_smoke():
    from src.agents.reporter import build_report
    r = build_report([])
    assert r["app"] == "Oggy Organizer"
