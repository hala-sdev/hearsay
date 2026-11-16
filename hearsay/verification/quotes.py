def quote_handling(quote, passage_text):
    text = quote.replace("…", "...")
    text = text.replace("(...)", "...")
    text = text.replace("[...]", "...")

    pieces = [p.strip() for p in text.split("...") if p.strip()]
    if not pieces:
        return False

    pos = 0
    for piece in pieces:
        found = passage_text.find(piece, pos)
        if found == -1:
            return False
        pos = found + len(piece)

    return True
