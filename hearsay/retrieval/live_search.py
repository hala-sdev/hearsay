from hearsay.retrieval.wiki_passages import get_passages, wiki 
from hearsay.retrieval.indexer import create_collection, upload_passages
from qdrant_client import QdrantClient
from hearsay.retrieval.retriever import search

def live_search(claim):
    result = wiki.search(claim, limit=2)
    all_passages = []
    for r in result.pages:
        passages = get_passages(r)
        all_passages.extend(passages)

    if not all_passages:
        return []

    client = QdrantClient(":memory:")
    collection_name = "live"
    create_collection(client, collection_name)
    upload_passages(client, collection_name, all_passages)
    return search(claim, client = client, collection = collection_name)

if __name__ == "__main__":
    result = live_search("Genshin Impact is a game developed by miHoYo")
    for r in result:
        print(r["path"])
        print(r["text"][:200])

