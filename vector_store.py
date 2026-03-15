import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# ------------------ LOAD MODEL ------------------
model = SentenceTransformer("all-MiniLM-L6-v2")

dimension = 384
index = faiss.IndexFlatL2(dimension)

# Metadata storage
documents = []


# ------------------ CHUNKING ------------------
def chunk_text(text: str, chunk_size: int = 300, overlap: int = 50):

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


# ------------------ EMBEDDING ------------------
def embed_text(text: str):
    embedding = model.encode(text)
    return np.array(embedding).astype("float32")


# ------------------ ADD DOCUMENT ------------------
def add_document(doc_id: int, content: str):

    chunks = chunk_text(content)

    if not chunks:
        return

    for chunk in chunks:

        embedding = embed_text(chunk)

        index.add(np.array([embedding]))

        documents.append({
            "doc_id": doc_id,
            "content": chunk
        })


# ------------------ SEARCH ------------------
def search(query: str, document_id: int = None, top_k: int = 5):

    if index.ntotal == 0:
        return []

    query_vector = np.array([embed_text(query)])

    D, I = index.search(query_vector, top_k)

    results = []

    for idx in I[0]:

        if idx < 0 or idx >= len(documents):
            continue

        doc = documents[idx]

        if document_id is not None and doc["doc_id"] != document_id:
            continue

        results.append(doc["content"])

    return results