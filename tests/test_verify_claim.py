from hearsay.verification import verifier

qdrant_pass = [{"id": "p1", "path": "Some article", "text": "Unrelated text."}]
live_pass = [{"id": "w1", "path": "Genshin Impact", "text": "Genshin Impact is a 2020 video game."}]


def test_nei_triggers_fallback_and_keeps_first_pass(monkeypatch):
    nei = {"claim": "c", "label": "NOT ENOUGH INFO", "reasoning": "no info", "cited": []}
    supports = {"claim": "c", "label": "SUPPORTS", "reasoning": "found it", "cited": []}
    answers = [nei, supports]
    live_calls = []

    def fake_search(claim, k, candidates):
        return qdrant_pass

    def fake_live_search(claim):
        live_calls.append(claim)
        return live_pass

    def fake_judge(claim, passages):
        return answers.pop(0)

    monkeypatch.setattr(verifier, "search", fake_search)
    monkeypatch.setattr(verifier, "live_search", fake_live_search)
    monkeypatch.setattr(verifier, "judge", fake_judge)

    result = verifier.verify_claim("Genshin Impact is a 2020 game.")

    assert result["label"] == "SUPPORTS"
    assert result["retried"] is True
    assert result["first_pass"]["label"] == "NOT ENOUGH INFO"
    assert len(live_calls) == 1


def test_supports_does_not_trigger_fallback(monkeypatch):
    supports = {"claim": "c", "label": "SUPPORTS", "reasoning": "found it", "cited": []}
    answers = [supports]
    live_calls = []

    def fake_search(claim, k, candidates):
        return qdrant_pass

    def fake_live_search(claim):
        live_calls.append(claim)
        return live_pass

    def fake_judge(claim, passages):
        return answers.pop(0)

    monkeypatch.setattr(verifier, "search", fake_search)
    monkeypatch.setattr(verifier, "live_search", fake_live_search)
    monkeypatch.setattr(verifier, "judge", fake_judge)

    result = verifier.verify_claim("Genshin Impact is a 2020 game.")

    assert result["label"] == "SUPPORTS"
    assert result["retried"] is False
    assert len(live_calls) == 0


def test_empty_live_search_keeps_nei(monkeypatch):
    nei = {"claim": "c", "label": "NOT ENOUGH INFO", "reasoning": "no info", "cited": []}
    answers = [nei]
    live_calls = []

    def fake_search(claim, k, candidates):
        return qdrant_pass

    def fake_live_search(claim):
        live_calls.append(claim)
        return []

    def fake_judge(claim, passages):
        return answers.pop(0)

    monkeypatch.setattr(verifier, "search", fake_search)
    monkeypatch.setattr(verifier, "live_search", fake_live_search)
    monkeypatch.setattr(verifier, "judge", fake_judge)

    result = verifier.verify_claim("Genshin Impact is a 2020 game.")

    assert result["label"] == "NOT ENOUGH INFO"
    assert result["retried"] is False
    assert len(live_calls) == 1