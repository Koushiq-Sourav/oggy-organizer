def test_structure():
    from src.agents.structure import check_structure
    r = check_structure("abstract introduction literature methodology implementation testing conclusion reference declaration acknowledgement", [])
    assert r["score"] >= 60


def test_slides():
    from src.agents.slides import check_slides
    r = check_slides([{"n": 1, "bullets": ["a"], "notes": "n"}])
    assert r["slides"] == 1
