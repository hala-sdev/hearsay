from hearsay.extraction.checks import remove_duplicates, leftover_pronouns

def test_remove_duplicates_drops_copies():
    claims = ["Paris is in France.", "paris is in france", "Rome is in Italy."]
    result = remove_duplicates(claims)
    assert result == ["Paris is in France.", "Rome is in Italy."]

def test_remove_duplicates_keeps_different_claims():
    claims = ["Paris is in France.", "Rome is in Italy."]
    result = remove_duplicates(claims)
    assert result == ["Paris is in France.", "Rome is in Italy."]


def test_leftover_pronouns_finds_capitalized_she():
    claims = "She won two Nobel Prizes."
    result = leftover_pronouns(claims)
    assert result == ["she"]

def test_leftover_pronouns_strips_punctuation():
    claims = "The award went to him."
    result = leftover_pronouns(claims)
    assert result == ["him"]


def test_leftover_pronouns_ignores_pronoun_inside_word():
    claims = "Einestin visited Italy"
    result = leftover_pronouns(claims)
    assert result == []



