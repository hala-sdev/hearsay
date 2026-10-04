from qdrant_client import QdrantClient, models
from hearsay.config import qdrant_api, qdrant_url
from fastembed import TextEmbedding, SparseTextEmbedding

client = QdrantClient(url=qdrant_url, api_key=qdrant_api)

collection_name = "wiki_passages"
dense_embedding_model = "BAAI/bge-small-en-v1.5"   
sparse_embedding_model = "Qdrant/bm25"

dense_embedder = TextEmbedding(model_name=dense_embedding_model)
sparse_embedder = SparseTextEmbedding(model_name=sparse_embedding_model)

claim = "Genshin Impact is a book"

dense_embeddings = list(dense_embedder.query_embed([claim]))
sparse_embeddings = list(sparse_embedder.query_embed([claim]))


sparse_vec = models.SparseVector(
        indices=sparse_embeddings[0].indices.tolist(),
        values=sparse_embeddings[0].values.tolist())


results = client.query_points(
    collection_name=collection_name,
    prefetch=[
        models.Prefetch(query=dense_embeddings[0].tolist(), using="bge_small", limit=20),
        models.Prefetch(query=sparse_vec, using="bm25", limit=20),
    ],
    query=models.FusionQuery(fusion=models.Fusion.RRF),
    limit=5,
)

print("Results for claim:", claim)
for r in results.points:
    print("\nArticle Path:",r.payload["path"], "Score:", r.score, "Text:", r.payload["text"])