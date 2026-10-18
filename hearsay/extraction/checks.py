

pronouns = {"he", "she", "it", "they", "him", "her", "them", "his", "its", "their"}

def ungrounded_terms(claim, text):
    flagged = []
    for word in claim.split():
        word = word.strip(".,;:!?\"'()")
        if not word:
            continue
        if (word[0].isupper() or word[0].isdigit()) and word.lower() not in text.lower():
            flagged.append(word)
    return flagged


def leftover_pronouns(claim):
    flagged = []
    for word in claim.split():
        word = word.strip(".,;:!?\"'()")
        if not word:
            continue
        if word.lower() in pronouns:
            flagged.append(word.lower())  
    return flagged

def normalize(claim):
    cleaned_claim = []
    for word in claim.split():
        word = word.strip(".,;:!?\"'()")
        if not word:
            continue
        word = word.lower()
        cleaned_claim.append(word)
    return " ".join(cleaned_claim)    

def remove_duplicates(claims):
    seen =set()
    kept = []
    for claim in claims:
        result = normalize(claim)
        if result not in seen:
            seen.add(result)
            kept.append(claim)
    return kept

if __name__ == "__main__":
    text = "Marie Curie was born in Warsaw in 1867. She won two Nobel Prizes."
    claims = [
        "Marie Curie was born in Warsaw in 1867.",
        "Marie Curie won two Nobel Prizes in 1903.",
        "Marie Curie was born in Paris.",
        "Pierre Curie won two Nobel Prizes.",
    ]
    for c in claims:
        print(c, "→", ungrounded_terms(c, text))

    pronoun_claims = [
    "Marie Curie won two Nobel Prizes.",
    "She won two Nobel Prizes.",
    "Marie Curie married Pierre Curie, and he was a physicist.",
    "Their daughter Irène won a Nobel Prize.",
    "The Shelby museum is in Warsaw.",
    ]
    for c in pronoun_claims:
        print(c, "→", leftover_pronouns(c)) 

    dup_claims = [
    "Marie Curie won two Nobel Prizes.",
    "Marie Curie was born in Warsaw.",
    "marie curie won two Nobel Prizes",
    "Marie Curie  won two Nobel Prizes.",
    "Marie Curie won 2 Nobel prizes.",
    ]
    print(remove_duplicates(dup_claims))