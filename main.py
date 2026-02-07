from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# ✅ CORS FIX (VERY IMPORTANT)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # allow frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Request Model ----------
class AskRequest(BaseModel):
    document: str
    question: str

# ---------- Health Check ----------
@app.get("/ping")
def ping():
    return {"status": "Backend OK"}

# ---------- CORE LOGIC ----------
@app.post("/ask")
def ask_doc(data: AskRequest):
    document = data.document.lower()
    question = data.question.lower()

    question_words = question.split()
    lines = document.splitlines()

    matched_lines = []

    for line in lines:
        for word in question_words:
            if word in line:
                matched_lines.append(line.strip())
                break

    if not matched_lines:
        return {
            "answer": "❌ No relevant content found in the document."
        }

    return {
        "answer": "✅ Relevant content found:\n\n" + "\n".join(matched_lines[:5])
    }