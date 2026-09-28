def test_q1_word_refs():
    from src.agents.q1_reviewer import check_q1
    from src.agents.word_choice import check_words
    from src.agents.refs_checker import check_refs
    assert "q1" in check_q1("gap limitation method result novel contribution", [] )["agent"]
    assert "word" in check_words("clear academic text")["agent"]
    assert "refs" in check_refs("Intro\n\nReferences\n[1] A. Author, Title, Journal, 2024, doi:10.1/x")["agent"]
