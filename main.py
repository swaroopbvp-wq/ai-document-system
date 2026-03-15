from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import init_db, insert_document, insert_query, get_connection
from vector_store import add_document, search

import pdfplumber
from docx import Document
import io


# ------------------ FASTAPI APP ------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------ INIT DATABASE ------------------
init_db()


# ------------------ LOAD FAISS FROM DB ON START ------------------
@app.on_event("startup")
def load_existing_documents():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, content FROM documents")
    rows = cursor.fetchall()

    conn.close()

    for row in rows:
        if row["content"]:  # avoid empty documents
            add_document(row["id"], row["content"])

    print(f"Loaded {len(rows)} documents into FAISS.")


# ------------------ REQUEST MODELS ------------------
class AskRequest(BaseModel):
    document_id: int
    question: str


# ------------------ HEALTH CHECK ------------------
@app.get("/ping")
def ping():
    return {"status": "Backend OK"}


# ------------------ UPLOAD DOCUMENT ------------------
@app.post("/upload")
async def upload_doc(file: UploadFile = File(...)):

    filename = file.filename.lower()
    raw_content = await file.read()

    extracted_text = ""

    try:

        # TXT
        if filename.endswith(".txt"):
            extracted_text = raw_content.decode("utf-8")

        # PDF
        elif filename.endswith(".pdf"):
            with pdfplumber.open(io.BytesIO(raw_content)) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        extracted_text += text + "\n"

        # DOCX
        elif filename.endswith(".docx"):
            doc = Document(io.BytesIO(raw_content))
            for para in doc.paragraphs:
                extracted_text += para.text + "\n"

        else:
            return {"message": "Unsupported file format"}

    except Exception as e:
        print("Extraction error:", e)
        return {"message": "Document parsing failed"}

    # ---------- DEBUG ----------
    print("Extracted text length:", len(extracted_text))
    print("Preview:", extracted_text[:300])
    # ---------------------------

    # Prevent empty documents
    if not extracted_text.strip():
        return {"message": "No readable text found in document"}

    # Save to database
    doc_id = insert_document(filename, extracted_text)

    # Add to FAISS
    add_document(doc_id, extracted_text)

    return {
        "message": "Document uploaded successfully",
        "document_id": doc_id
    }


# ------------------ ASK (LOCAL RAG MODE) ------------------
@app.post("/ask")
def ask_doc(data: AskRequest):

    print("\n--- NEW ASK REQUEST ---")
    print("Document ID:", data.document_id)
    print("Question:", data.question)

    chunks = search(
        query=data.question,
        document_id=data.document_id
    )

    print("Retrieved chunks:", chunks)
    print("Chunks count:", len(chunks))

    if not chunks:
        answer = "No relevant content found in this document."
    else:
        answer = "\n\n".join(chunks)

    # Save history
    insert_query(data.document_id, data.question, answer)

    return {"answer": answer}


# ------------------ GET HISTORY ------------------
@app.get("/history/{document_id}")
def get_history(document_id: int):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT question, answer, asked_at
        FROM queries
        WHERE document_id = ?
        ORDER BY asked_at DESC
        """,
        (document_id,)
    )

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return {"message": "No history found for this document."}

    return [
        {
            "question": row["question"],
            "answer": row["answer"],
            "asked_at": row["asked_at"]
        }
        for row in rows
    ]