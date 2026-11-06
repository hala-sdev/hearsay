import json
import numpy as np

from hearsay.retrieval.retriever import search
LIMIT = None
records = []
with open("eval/fever_retrieval.jsonl", "r", encoding="utf-8") as file:
    for line in file:

        row = json.loads(line)
        records.append(row)

all_count = 0
num_supports = 0
num_refutes = 0
refutes_5 = 0
supports_5 = 0
refutes_20 = 0
supports_20 = 0
for row in records[:LIMIT]:

    claim = row["claim"]
    group = row["group"]
    results = search(claim, k=20, candidates=20)
    articles = []
    for r in results:
        articles.append(r["article"])
    top_5 = articles[:5]
    top_20 = articles[:20]
    if any(article in row["pages"] for article in top_5):
        if group == "SUPPORTS":
            supports_5 += 1
        elif group == "REFUTES":
            refutes_5 += 1
    if any(article in row["pages"] for article in top_20):
        if group == "SUPPORTS":
            supports_20 += 1
        elif group == "REFUTES":
            refutes_20 += 1

    if group == "SUPPORTS":
        num_supports += 1
    elif group == "REFUTES":
        num_refutes += 1
    all_count += 1

    if all_count % 100 == 0:
        print(all_count)


recall_5 = (supports_5 + refutes_5) / all_count if all_count > 0 else 0
recall_20 = (supports_20 + refutes_20) / all_count if all_count > 0 else 0

recall_5_supports = supports_5 / num_supports if num_supports > 0 else 0
recall_5_refutes = refutes_5 / num_refutes if num_refutes > 0 else 0

recall_20_supports = supports_20 / num_supports if num_supports > 0 else 0
recall_20_refutes = refutes_20 / num_refutes if num_refutes > 0 else 0

print(f"Recall@5: {recall_5:.4f}")
print(f"Recall@20: {recall_20:.4f}")
print(f"Recall@5 (Supports): {recall_5_supports:.4f}")
print(f"Recall@5 (Refutes): {recall_5_refutes:.4f}")
print(f"Recall@20 (Supports): {recall_20_supports:.4f}")
print(f"Recall@20 (Refutes): {recall_20_refutes:.4f}")