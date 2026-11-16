
from hearsay.verification.quotes import quote_handling

# Adapted from the Wikipedia article "Genshin Impact" (CC BY-SA)
passage = (
    "Genshin Impact is a 2020 action role-playing video game developed and "
    "published by miHoYo. It was originally released for Android, iOS, "
    "PlayStation 4, and Windows, followed by the PlayStation 5 in 2021, and "
    "Xbox Series X/S in 2024."
)

def test_exact_quote_is_verified():
    quote = "developed and published by miHoYo"
    result = quote_handling(quote, passage)
    assert result is True

def test_quote_with_gap_in_order_is_verified():
    quote = "Genshin Impact is a 2020 (...) video game"
    result = quote_handling(quote, passage)
    assert result is True


def test_pieces_in_wrong_order_are_rejected():
    quote = "followed by the PlayStation 5 in 2021 (...) Genshin Impact is a 2020"
    result = quote_handling(quote, passage)
    assert result is False 

def test_changed_number_is_rejected():
    quote = "followed by the PlayStation 5 in 2022"
    result = quote_handling(quote, passage)
    assert result is False 

def test_empty_quote_is_rejected():
    quote = "(...)"
    result = quote_handling(quote, passage)
    assert result is False 