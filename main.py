from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import init_db, insert_document, insert_query, get_connection
import re

app = FastAPI()

# ---------- CORS ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- INIT DB ----------
init_db()

# ---------- REQUEST MODELS ----------
class UploadRequest(BaseModel):
    filename: str
    content: str


class AskRequest(BaseModel):
    document_id: int
    question: str


# ---------- HEALTH CHECK ----------
@app.get("/ping")
def ping():
    return {"status": "Backend OK"}


# ---------- STEP 4B: FACT EXTRACTION ----------
def extract_facts(document: str):
    facts = {}

    # Invoice Date
    date_match = re.search(
        r"(invoice\s*date|date)\s*(is|:|-)?\s*([a-z0-9\s]+)",
        document,
        re.I
    )
    if date_match:
        facts["invoice_date"] = date_match.group(3).strip()

    # Total Amount (handles "is", currency, words)
    amount_match = re.search(
        r"(total\s*amount)\s*(is|:|-)?\s*(\d+)",
        document,
        re.I
    )
    if amount_match:
        facts["total_amount"] = amount_match.group(3).strip()

    return facts


# ---------- UPLOAD DOCUMENT ----------
@app.post("/upload")
def upload_doc(data: UploadRequest):
    doc_id = insert_document(data.filename, data.content)
    return {
        "message": "✅ Document uploaded successfully",
        "document_id": doc_id
    }


# ---------- STEP 4C + TEST 3 ----------
@app.post("/ask")
def ask_doc(data: AskRequest):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT content FROM documents WHERE id = ?",
        (data.document_id,)
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        return {"answer": "❌ Document not found"}

    document = row["content"]
    question = data.question.lower()

    facts = extract_facts(document)

    # ---------- DETERMINISTIC ANSWERING ----------
    if "date" in question:
        if "invoice_date" in facts:
            answer = f"The invoice date is {facts['invoice_date']}."
        else:
            answer = "❌ Invoice date not found in the document."

    elif "total" in question or "amount" in question:
        if "total_amount" in facts:
            answer = f"The total amount is {facts['total_amount']} rupees."
        else:
            answer = "❌ Total amount not found in the document."

    else:
        answer = "❌ I don't understand this question yet."

    insert_query(data.document_id, data.question, answer)
    return {"answer": answer}