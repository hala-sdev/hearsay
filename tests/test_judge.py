from hearsay.verification import verifier
from hearsay.verification.verifier import VerificationResult, Statement

PASSAGES = [
    {"id": "p1", "path": "Genshin Impact > Summary",
     "text": "Genshin Impact is a 2020 action role-playing video game developed and published by miHoYo."}
]


def test_unverified_quote_downgrades_supports_to_nei(monkeypatch):
    fake_answer = VerificationResult(
        reasoning="The evidence says it was released in 2026.",
        evidence=[Statement(pass_number=1, quote="released in 2026")],
        label="SUPPORTS",
    )

    def fake_ask_gemini(claim, passages):
        return fake_answer

    monkeypatch.setattr(verifier, "ask_gemini", fake_ask_gemini)

    result = verifier.judge("Genshin Impact was released in 2026.", PASSAGES)

    assert result["label"] == "NOT ENOUGH INFO"
    assert result["cited"][0]["verified"] is False



def test_verified_quote_keeps_supports(monkeypatch):
    fake_answer = VerificationResult(
        reasoning="The evidence says it was developed and published by miHoYo",
        evidence=[Statement(pass_number=1, quote="developed and published by miHoYo")],
        label="SUPPORTS",
    )

    def fake_ask_gemini(claim, passages):
        return fake_answer

    monkeypatch.setattr(verifier, "ask_gemini", fake_ask_gemini)

    result = verifier.judge("Genshin Impact was developed and published by miHoYo", PASSAGES)

    assert result["label"] == "SUPPORTS"
    assert result["cited"][0]["verified"] is True


def test_out_of_range_passage_number_is_ignored(monkeypatch):
    fake_answer = VerificationResult(
        reasoning="The evidence says it was released in 2026.",
        evidence=[Statement(pass_number=5, quote="released in 2026")],
        label="SUPPORTS",
    )

    def fake_ask_gemini(claim, passages):
        return fake_answer

    monkeypatch.setattr(verifier, "ask_gemini", fake_ask_gemini)

    result = verifier.judge("Genshin Impact was released in 2026.", PASSAGES)

    assert result["label"] == "NOT ENOUGH INFO"
    assert result["cited"] == []


def test_gemini_failure_gives_error_label(monkeypatch):
    def failing_ask_gemini(claim, passages):
        raise RuntimeError("Gemini is down")

    monkeypatch.setattr(verifier, "ask_gemini", failing_ask_gemini)

    result = verifier.judge("Genshin Impact was released in 2020.", PASSAGES)

    assert result["label"] == "ERROR"
    assert "Gemini is down" in result["reasoning"]