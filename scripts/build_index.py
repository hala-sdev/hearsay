from hearsay.retrieval.wiki_passages import get_passages
from qdrant_client import QdrantClient, models
from hearsay.config import qdrant_api, qdrant_url


client = QdrantClient(url=qdrant_url, api_key=qdrant_api)

collection_name = "wiki_passages"
dense_embedding_model = "BAAI/bge-small-en-v1.5"   
sparse_embedding_model = "Qdrant/bm25"

if not client.collection_exists(collection_name):

    client.create_collection(
        collection_name=collection_name,
        vectors_config={"bge_small": models.VectorParams(
            size=384,
            distance=models.Distance.COSINE
        )},
        sparse_vectors_config={"bm25": models.SparseVectorParams(modifier=models.Modifier.IDF)}
    )






