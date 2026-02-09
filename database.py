import sqlite3
from datetime import datetime

DB_NAME = "documents.db"


# ---------- Get DB Connection ----------
def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


# ---------- Initialize Database ----------
def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Documents table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            content TEXT NOT NULL,
            uploaded_at TEXT NOT NULL
        )
    """)

    # Queries table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            asked_at TEXT NOT NULL,
            FOREIGN KEY (document_id) REFERENCES documents(id)
        )
    """)

    conn.commit()
    conn.close()


# ---------- Insert Document ----------
def insert_document(filename, content):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO documents (filename, content, uploaded_at)
        VALUES (?, ?, ?)
    """, (filename, content, datetime.now().isoformat()))

    conn.commit()
    doc_id = cursor.lastrowid
    conn.close()
    return doc_id


# ---------- Insert Query ----------
def insert_query(document_id, question, answer):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO queries (document_id, question, answer, asked_at)
        VALUES (?, ?, ?, ?)
    """, (document_id, question, answer, datetime.now().isoformat()))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully")    