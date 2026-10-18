from hearsay.retrieval.retriever import cloud_client
from hearsay.config import collection_name

info = cloud_client.get_collection(collection_name)
print(info.status, info.points_count)