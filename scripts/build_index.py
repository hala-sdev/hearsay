from hearsay.retrieval.wiki_passages import get_passages
from collections import Counter
from qdrant_client import QdrantClient
from hearsay.config import qdrant_api, qdrant_url

client = QdrantClient(url=qdrant_url, api_key=qdrant_api)
print(client.get_collections())




