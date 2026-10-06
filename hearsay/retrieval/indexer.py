from hearsay.config import dense_embedding_model, sparse_embedding_model, dense_vector_name, sparse_vector_name
from fastembed import TextEmbedding, SparseTextEmbedding
from qdrant_client import models
dense_embedder = TextEmbedding(model_name=dense_embedding_model)
sparse_embedder = SparseTextEmbedding(model_name=sparse_embedding_model)

def create_collection(client, collection_name):
    if not client.collection_exists(collection_name):
        client.create_collection(
            collection_name=collection_name,
            vectors_config={dense_vector_name: models.VectorParams(
                size=384,
                distance=models.Distance.COSINE
            )},
            sparse_vectors_config={sparse_vector_name: models.SparseVectorParams(modifier=models.Modifier.IDF)}
        )

def upload_passages(client, collection_name, passages):
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