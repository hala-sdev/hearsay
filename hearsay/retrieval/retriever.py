from qdrant_client import QdrantClient, models
from hearsay.config import qdrant_api, qdrant_url, collection_name, dense_embedding_model, sparse_embedding_model,dense_vector_name, sparse_vector_name
from fastembed import TextEmbedding, SparseTextEmbedding

client = QdrantClient(url=qdrant_url, api_key=qdrant_api)


dense_embedder = TextEmbedding(model_name=dense_embedding_model)
sparse_embedder = SparseTextEmbedding(model_name=sparse_embedding_model)

def search(claim, k = 5, candidates = 20):
    dense_embeddings = list(dense_embedder.query_embed([claim]))
    sparse_embeddings = list(sparse_embedder.query_embed([claim]))


    sparse_vec = models.SparseVector(
            indices=sparse_embeddings[0].indices.tolist(),
            values=sparse_embeddings[0].values.tolist())


    results = client.query_points(
        collection_name=collection_name,
        prefetch=[
            models.Prefetch(query=dense_embeddings[0].tolist(), using=dense_vector_name, limit=candidates),
            models.Prefetch(query=sparse_vec, using=sparse_vector_name, limit=candidates),
        ],
        query=models.FusionQuery(fusion=models.Fusion.RRF),
        limit=k,
    )

    results_list = []
    for r in results.points:
        results_list.append({
            "id": r.id,
            "article": r.payload["article"],
            "path": r.payload["path"],
            "score": r.score,
            "text": r.payload["text"]
        })
    return results_list

if __name__ == "__main__":
    results = search("Albert Einstein was a physicist", k=3, candidates=20)
    print("Results for claim:", "Albert Einstein was a physicist")
    for r in results:
        print("\nArticle:",r["path"], "Score:", r["score"], "Text:", r["text"])