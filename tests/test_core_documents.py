"""Unit tests for core.documents — text extraction and the document index."""
import io

import pytest
from docx import Document

from core.documents import (
    delete_document,
    extract_text_from_bytes,
    get_combined_document_text,
    get_documents,
    process_and_store_document,
)


def _make_docx(text: str) -> bytes:
    buf = io.BytesIO()
    doc = Document()
    doc.add_paragraph(text)
    doc.save(buf)
    return buf.getvalue()


def test_extract_text_from_txt_utf8():
    text = extract_text_from_bytes("notes.txt", "Héllo GrantPilot".encode("utf-8"))
    assert text == "Héllo GrantPilot"


def test_extract_text_from_txt_latin1_fallback():
    # Not valid UTF-8, but decodable as latin-1; the extractor falls back.
    raw = "café".encode("latin-1")
    assert extract_text_from_bytes("legacy.txt", raw) == "café"


def test_extract_text_from_docx():
    payload = _make_docx("Grant proposal draft inside a docx.")
    text = extract_text_from_bytes("draft.docx", payload)
    assert "Grant proposal draft inside a docx." in text


def test_extract_text_unsupported_extension_raises():
    with pytest.raises(ValueError, match="Unsupported file format"):
        extract_text_from_bytes("archive.zip", b"PK\x05\x06")


def test_process_and_store_txt_document(data_dir):
    result = process_and_store_document(
        "mission.txt", b"Help museums digitize their collections."
    )
    assert result["filename"] == "mission.txt"
    assert result["word_count"] == 5
    assert result["char_count"] == len("Help museums digitize their collections.")
    # Indexed and persisted under the generated short id.
    docs = get_documents()
    assert any(d["id"] == result["id"] for d in docs)


def test_process_and_store_empty_file_rejected(data_dir):
    with pytest.raises(ValueError, match="appears to be empty"):
        process_and_store_document("empty.txt", b"")


def test_delete_document(data_dir):
    result = process_and_store_document("bye.txt", b"temporary content here")
    doc_id = result["id"]
    assert delete_document(doc_id) is True
    assert delete_document(doc_id) is False
    assert get_documents() == []


def test_get_documents_missing_file(data_dir):
    # Fresh data_dir with no documents.json yet.
    assert get_documents() == []


def test_get_combined_document_text_joins_documents(data_dir):
    process_and_store_document("a.txt", b"alpha beta gamma")
    process_and_store_document("b.txt", b"delta epsilon zeta")
    combined = get_combined_document_text()
    assert "=== DOCUMENT: a.txt ===" in combined
    assert "alpha beta gamma" in combined
    assert "delta epsilon zeta" in combined


def test_get_combined_document_text_truncates(data_dir):
    process_and_store_document("a.txt", b"alpha beta gamma")
    process_and_store_document("b.txt", b"delta epsilon zeta")
    full = get_combined_document_text()
    # Budget only large enough for the first document's snippet.
    first_snippet_len = len(full.split("\n\n")[0]) + 1  # plus trailing newline
    truncated = get_combined_document_text(max_chars=first_snippet_len + 4)
    assert "alpha beta gamma" in truncated
    assert "delta epsilon zeta" not in truncated


def test_get_combined_document_text_no_documents(data_dir):
    assert get_combined_document_text() == ""
