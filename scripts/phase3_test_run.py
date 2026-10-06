import json
from hearsay.verification.verifier import verify_claim

test_claims = [
    ("The Eiffel Tower is in Paris", "SUPPORTS"),
    ("The Eiffel Tower is in Rome", "REFUTES"),
    ("The Amazon River is in Africa", "REFUTES"),
    ("World War II ended in 1945", "SUPPORTS"),
    ("World War II ended in 1946", "REFUTES"),
    ("Mount Everest is over 8,000 metres tall", "SUPPORTS"),
    ("Marie Curie won Nobel Prizes in two different sciences", "SUPPORTS"),
    ("Apollo 11 landed on the Moon in 1969", "SUPPORTS"),
    ("William Shakespeare wrote Hamlet", "SUPPORTS"),
    ("The Pacific Ocean is the smallest ocean on Earth", "REFUTES"),
    ("Photosynthesis releases oxygen", "SUPPORTS"),
    ("Water boils at 50 degrees Celsius at sea level", "REFUTES"),
    ("Leonardo da Vinci painted the Mona Lisa", "SUPPORTS"),
    ("The Berlin Wall fell in 1989", "SUPPORTS"),
    ("Albert Einstein won the Nobel Prize for the theory of relativity", "REFUTES"),
    ("Hollow Knight was developed by Team Cherry", "SUPPORTS"),
    ("Genshin Impact is a game developed by miHoYo", "SUPPORTS"),
    ("Some scientists disagree about many things", "NOT ENOUGH INFO"),
]

results = []
matches = 0
retried = 0
errors = 0
unverified = 0

for claim, expected in test_claims:
    result = verify_claim(claim)
    result["expected"] = expected
    results.append(result)

    if result["label"] == expected:
        matches += 1
    if result["retried"]:
        retried += 1
    if result["label"] == "ERROR":
        errors += 1
    for item in result["cited"]:
        if not item["verified"]:
            unverified += 1

    mark = "correct  " if result["label"] == expected else "wrong   "
    print(f"{mark} {claim}")
    print(f"   expected: {expected} | got: {result['label']} | retried: {result['retried']}")


print(f"\n\n\nMatched expected: {matches}/{len(test_claims)}")
print(f"Used live retry:  {retried}")
print(f"Errors:           {errors}")
print(f"Unverified quotes in final results: {unverified}")

with open("data/phase3_test_run.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)