from hearsay.retrieval.wiki_passages import get_passages
from qdrant_client import QdrantClient
from hearsay.config import qdrant_api, qdrant_url, collection_name
from hearsay.retrieval.indexer import create_collection, upload_passages
import json
import time
import os

client = QdrantClient(url=qdrant_url, api_key=qdrant_api, timeout=60)


with open("data/titles.json", "r",encoding="utf-8") as f:
    titles = json.load(f)

all_titles = []
for s in titles:
    all_titles.extend(titles[s])

create_collection(client, collection_name)

if os.path.exists("data/done_titles.txt"):
    with open("data/done_titles.txt", "r", encoding="utf-8") as f:
        done_titles = set(f.read().splitlines())
else:
    done_titles = set()



for i in range(0, len(all_titles), 50):
    batch_titles = all_titles[i:i+50]
    qdrant_passages = []
    start_time = time.time()

    for title in batch_titles:
        if title in done_titles:
            continue
        try:
            passages = get_passages(title)
        except Exception as e:
            with open("data/failed_titles.txt", "a", encoding="utf-8") as f:
                f.write(f"{title} | {e}\n")
                continue

        if passages:
            qdrant_passages.extend(passages)
        else:
            with open("data/failed_titles.txt", "a", encoding="utf-8") as f:
                        f.write(title + "\n")

    if qdrant_passages:
        upload_passages(client, collection_name, qdrant_passages)
        with open("data/done_titles.txt", "a", encoding="utf-8") as f:
            f.write("\n".join(batch_titles) + "\n")        
    end_time = time.time()
    print(f"Progress: {i + len(batch_titles)}/{len(all_titles)} titles processed. Time taken for this batch: {end_time - start_time:.2f} seconds.")


print(client.count(collection_name=collection_name))