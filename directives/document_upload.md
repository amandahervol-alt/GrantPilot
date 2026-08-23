# Directive: Document Upload & Indexing

**Goal:** Ingest documents (PDF, DOCX, TXT) provided by the user, parse their raw text, and index the content into the local document store to enrich organizational memory and funder matching.

**Inputs:**
- Raw file stream/upload (PDF, DOCX, or TXT).
- Original filename and metadata.

**Tools/Scripts to use:**
- `execution/parse_document.py` - Core extraction and indexing script.
- `core/documents.py` - Document storage, file parser wrappers, and text sanitization.

**Outputs:**
- Document text saved and registered in `data/documents.json`.
- Parsed metadata returned to user (document ID, filename, extracted character/word count, timestamp).

**Edge Cases & Rules:**
- Unsupported File Formats: Reject non-PDF/DOCX/TXT files with a clear error message.
- Empty or Corrupt Files: Gracefully catch parsing exceptions (e.g. password-protected or unreadable PDFs) and return a friendly user message.
- Sanitization: Strip control characters, excess blank lines, and normalize whitespace before indexing.
- Storage: Save raw uploads in `.tmp/uploads/` if needed for reference, and store extracted structured text in `data/documents.json`.
