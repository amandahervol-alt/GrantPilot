from typing import Dict
from core.documents import process_and_store_document, get_documents, delete_document

def execute(filename: str, file_bytes: bytes) -> Dict:
    """
    Executes Workflow B: Document Parsing and Indexing.
    Extracts text from PDF/DOCX/TXT bytes and updates the document store.
    """
    return process_and_store_document(filename, file_bytes)

def list_indexed_documents():
    """Lists all currently indexed documents."""
    return get_documents()

def remove_document(doc_id: str) -> bool:
    """Removes a document from the index."""
    return delete_document(doc_id)

if __name__ == "__main__":
    # Test script with dummy text
    sample_text = "GrantPilot was established in 2024 to support nonprofit organizations in crafting competitive grant proposals."
    res = execute("test_overview.txt", sample_text.encode("utf-8"))
    print(f"Parsed and Indexed: {res['filename']} ({res['word_count']} words)")
