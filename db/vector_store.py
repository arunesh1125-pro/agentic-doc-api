import chromadb
from chromadb.config import Settings

client = chromadb.PersistentClient(path="./data/vector_store")
collection = client.get_or_create_collection("documents")

def add_document(doc_id, embedding, metadata):
    collection.add(
        ids=[doc_id],
        embeddings=[embedding],
        metadatas=[metadata]
    )

def search(embedding, top_k=5):
    results = collection.query(
        query_embeddings=[embedding],
        n_results=top_k
    )
    return results
def count():
    return collection.count()
