import json
from hearsay.retrieval.retriever import search
import os

os.makedirs("eval/results", exist_ok=True)

LIMIT = None
records = []
per_claim = []
with open("eval/fever_retrieval.jsonl", "r", encoding="utf-8") as file:
    for line in file:
        row = json.loads(line)
        records.append(row)

all_count = 0
num_count = {"SUPPORTS": 0, "REFUTES": 0}
hits_5 = {"SUPPORTS": 0, "REFUTES": 0}
hits_20 = {"SUPPORTS": 0, "REFUTES": 0}
for row in records[:LIMIT]:
    all_count += 1
    claim = row["claim"]
    group = row["group"]
    results = search(claim, k=20, candidates=20)
    articles = []
    for r in results:
        articles.append(r["article"])

    top_5 = articles[:5]
    hit_5_check = any(article in row["pages"] for article in top_5)
    hit_20_check = any(article in row["pages"] for article in articles)

    if hit_5_check:
        hits_5[group] += 1
    if hit_20_check:
        hits_20[group] += 1

    if group == "SUPPORTS":
        num_count[group] += 1
    elif group == "REFUTES":
        num_count[group] += 1

    first_hit = None
    for rank, article in enumerate(articles, start=1):
        if article in row["pages"]:
            first_hit = rank
            break

    per_claim.append({
        "id": row["id"],
        "claim": claim,
        "group": group,
        "pages": row["pages"],
        "top_5": top_5,
        "hits_5": hit_5_check,
        "hits_20": hit_20_check,
        "first_hit": first_hit
    })

    if all_count % 100 == 0:
        print(all_count)


with open("eval/results/retrieval_results.jsonl", "w", encoding="utf-8") as file:
    for row in per_claim:
        file.write(json.dumps(row, ensure_ascii=False) + "\n")

recall_5 = (hits_5["SUPPORTS"] + hits_5["REFUTES"]) / all_count if all_count > 0 else 0
recall_20 = (hits_20["SUPPORTS"] + hits_20["REFUTES"]) / all_count if all_count > 0 else 0

recall_5_supports = hits_5["SUPPORTS"] / num_count["SUPPORTS"] if num_count["SUPPORTS"] > 0 else 0
recall_5_refutes = hits_5["REFUTES"] / num_count["REFUTES"] if num_count["REFUTES"] > 0 else 0

recall_20_supports = hits_20["SUPPORTS"] / num_count["SUPPORTS"] if num_count["SUPPORTS"] > 0 else 0
recall_20_refutes = hits_20["REFUTES"] / num_count["REFUTES"] if num_count["REFUTES"] > 0 else 0

print(f"Recall@5: {recall_5:.4f}")
print(f"Recall@20: {recall_20:.4f}")
print(f"Recall@5 (Supports): {recall_5_supports:.4f}")
print(f"Recall@5 (Refutes): {recall_5_refutes:.4f}")
print(f"Recall@20 (Supports): {recall_20_supports:.4f}")
print(f"Recall@20 (Refutes): {recall_20_refutes:.4f}")
print(f"Total Claims Evaluated: {all_count}")