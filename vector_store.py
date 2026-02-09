import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# FAISS index
dimension = 384
index = faiss.IndexFlatL2(dimension)

# Store document chunks
documents = []


def embed_text(text: str):
    return model.encode([text])[0]


def add_document(doc_id: int, content: str):
    embedding = embed_text(content)
    index.add(np.array([embedding]).astype("float32"))
    documents.append({
        "doc_id": doc_id,
        "content": content
    })


def search(query: str, top_k: int = 3):
    if index.ntotal == 0:
        return []

    query_embedding = embed_text(query)
    D, I = index.search(np.array([query_embedding]).astype("float32"), top_k)

    results = []
    for i in I[0]:
        if i < len(documents):
            results.append(documents[i]["content"])

    return results