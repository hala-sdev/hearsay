import os
import json
from hearsay.verification.verifier import verify_claim


output_path = "eval/results/judge_results.jsonl"

LIMIT = None
records = []
per_claim = []
done_ids = set()

if os.path.exists(output_path):
    with open(output_path, "r", encoding="utf-8") as file:
        for line in file:
            row = json.loads(line)
            if row["pred_label"] != "ERROR":
                done_ids.add(row["id"])

with open("eval/fever_sample.jsonl", "r", encoding="utf-8") as file:
    for line in file:
        row = json.loads(line)
        records.append(row)

for row in records[:LIMIT]:
    if row["id"] in done_ids:
        continue
    claim = row["claim"]
    result = verify_claim(claim)
    correct = result["label"] == row["label"]
    per_claim.append({
        "id": row["id"],
        "group": row["group"],
        "claim": claim,
        "pred_label": result["label"],
        "gold_label": row["label"],
        "correct": correct,
        "num_cited": len(result["cited"]),
        "num_verified": sum(1 for c in result["cited"] if c["verified"]),
        "reasoning": result["reasoning"],
        "cited": result["cited"],
        "retried": result.get("retried", False),
        "first_pass": result["first_pass"]["label"] if result.get("first_pass") else None
    })

    print(row["id"], row["label"], result["label"])

    with open("eval/results/judge_results.jsonl", "a", encoding="utf-8") as file:
        file.write(json.dumps(per_claim[-1], ensure_ascii=False) + "\n")