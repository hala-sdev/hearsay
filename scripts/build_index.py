from hearsay.retrieval.wiki_passages import get_passages
from qdrant_client import QdrantClient, models
from hearsay.config import qdrant_api, qdrant_url, collection_name, dense_embedding_model, sparse_embedding_model, dense_vector_name, sparse_vector_name
from fastembed import TextEmbedding, SparseTextEmbedding
import json
import time
import os

client = QdrantClient(url=qdrant_url, api_key=qdrant_api, timeout=60)


with open("data/titles.json", "r",encoding="utf-8") as f:
    titles = json.load(f)

all_titles = []
for s in titles:
    all_titles.extend(titles[s])


dense_embedder = TextEmbedding(model_name=dense_embedding_model)
sparse_embedder = SparseTextEmbedding(model_name=sparse_embedding_model)

if not client.collection_exists(collection_name):
    client.create_collection(
        collection_name=collection_name,
        vectors_config={dense_vector_name: models.VectorParams(
            size=384,
            distance=models.Distance.COSINE
        )},
        sparse_vectors_config={sparse_vector_name: models.SparseVectorParams(modifier=models.Modifier.IDF)}
    )

if os.path.exists("data/done_titles.txt"):
    with open("data/done_titles.txt", "r", encoding="utf-8") as f:
        done_titles = set(f.read().splitlines())
else:
    done_titles = set()

def upload_passages_to_qdrant(passages):
    texts = [f"{p['path']}: {p['text']}" for p in passages]
    dense_embeddings = list(dense_embedder.embed(texts))
    sparse_embeddings = list(sparse_embedder.embed(texts))
    combined_embeddings = []
    for fetched_p, sparse, dense in zip(passages, sparse_embeddings, dense_embeddings):
        sparse_vec = models.SparseVector(
        indices=sparse.indices.tolist(),
        values=sparse.values.tolist())
    
        combined_embedding = models.PointStruct(
            id=fetched_p['id'],
            vector={dense_vector_name: dense.tolist(), sparse_vector_name: sparse_vec},
            payload={"article": fetched_p['article'], "path": fetched_p['path'], "text": fetched_p['text']}
        )
        combined_embeddings.append(combined_embedding)
    client.upsert(collection_name=collection_name, points=combined_embeddings)


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
        upload_passages_to_qdrant(qdrant_passages)
        with open("data/done_titles.txt", "a", encoding="utf-8") as f:
            f.write("\n".join(batch_titles) + "\n")        
    end_time = time.time()
    print(f"Progress: {i + len(batch_titles)}/{len(all_titles)} titles processed. Time taken for this batch: {end_time - start_time:.2f} seconds.")


print(client.count(collection_name=collection_name))