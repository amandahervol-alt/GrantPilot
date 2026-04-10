# Storage: SQLite (same DB as org data), documents table stores filename + extracted text.
# Reasoning: Keeps all persistence in a single file, no extra dependencies.
# Claude handles semantic relevance during matching — we just need full text available.
# TODO: If document count grows large (20+), consider ChromaDB for vector search to
# avoid hitting Claude's context window limits.

import sqlite3
import io
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "grantpilot.db"


def _get_conn():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_documents_db():
    with _get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                filename    TEXT NOT NULL,
                content     TEXT NOT NULL,
                char_count  INTEGER,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


def extract_text(filename: str, content: bytes) -> str:
    ext = Path(filename).suffix.lower()
    if ext == ".txt":
        return content.decode("utf-8", errors="replace")
    elif ext == ".pdf":
        try:
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(content))
            pages = [page.extract_text() or "" for page in reader.pages]
            return "\n\n".join(p for p in pages if p.strip())
        except ImportError:
            raise RuntimeError("pypdf is not installed. Run: pip install pypdf")
    elif ext == ".docx":
        try:
            import docx
            doc = docx.Document(io.BytesIO(content))
            return "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())
        except ImportError:
            raise RuntimeError("python-docx is not installed. Run: pip install python-docx")
    else:
        raise ValueError(f"Unsupported file type: {ext}. Please upload PDF, DOCX, or TXT.")


def save_document(filename: str, text: str) -> int:
    with _get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO documents (filename, content, char_count) VALUES (?, ?, ?)",
            (filename, text, len(text)),
        )
        conn.commit()
        return cur.lastrowid


def get_documents() -> list:
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT id, filename, char_count, uploaded_at FROM documents ORDER BY uploaded_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]


def delete_document(doc_id: int):
    with _get_conn() as conn:
        conn.execute("DELETE FROM documents WHERE id=?", (doc_id,))
        conn.commit()


def get_all_document_text() -> list:
    with _get_conn() as conn:
        rows = conn.execute("SELECT filename, content FROM documents").fetchall()
        return [dict(r) for r in rows]
