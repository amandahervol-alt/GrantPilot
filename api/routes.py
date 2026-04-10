from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from api.models import (
    SaveMemoryRequest,
    Program,
    ProgramUpdate,
    FunderMatchRequest,
    NarrativeRequest,
)
from core import memory as mem
from core import documents as docs
from core import matching
from core import narrative

router = APIRouter()


# ── Org Memory ──────────────────────────────────────────────────────────────

@router.get("/memory")
def get_memory():
    return mem.get_all_memory()


@router.put("/memory")
def save_memory(body: SaveMemoryRequest):
    mem.save_org_profile(body.profile.model_dump())
    mem.save_stats([s.model_dump() for s in body.stats])
    return {"status": "saved"}


# ── Programs ─────────────────────────────────────────────────────────────────

@router.get("/programs")
def get_programs():
    return mem.get_programs()


@router.post("/programs")
def add_program(body: Program):
    program_id = mem.add_program(body.model_dump())
    return {"id": program_id, **body.model_dump()}


@router.put("/programs/{program_id}")
def update_program(program_id: int, body: ProgramUpdate):
    mem.update_program(program_id, body.model_dump())
    return {"status": "updated"}


@router.delete("/programs/{program_id}")
def delete_program(program_id: int):
    mem.delete_program(program_id)
    return {"status": "deleted"}


# ── Documents ────────────────────────────────────────────────────────────────

@router.get("/documents")
def list_documents():
    return docs.get_documents()


@router.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    allowed = {".pdf", ".docx", ".txt"}
    from pathlib import Path
    ext = Path(file.filename).suffix.lower()
    if ext not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Please upload PDF, DOCX, or TXT.",
        )
    try:
        content = await file.read()
        text = docs.extract_text(file.filename, content)
        if not text.strip():
            raise HTTPException(
                status_code=422,
                detail="No text could be extracted from this file. It may be a scanned image or empty.",
            )
        doc_id = docs.save_document(file.filename, text)
        return {
            "id": doc_id,
            "filename": file.filename,
            "char_count": len(text),
            "preview": text[:300] + ("..." if len(text) > 300 else ""),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents/{doc_id}")
def delete_document(doc_id: int):
    docs.delete_document(doc_id)
    return {"status": "deleted"}


# ── Matching ─────────────────────────────────────────────────────────────────

@router.post("/match")
def match_funder(body: FunderMatchRequest):
    if not body.funder_priorities.strip():
        raise HTTPException(status_code=400, detail="Please enter the funder's priority areas.")
    try:
        result = matching.match_to_funder(body.funder_priorities)
        if "error" in result:
            raise HTTPException(status_code=422, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Matching failed: {str(e)}")


# ── Narrative ────────────────────────────────────────────────────────────────

@router.post("/narrative")
def generate_narrative(body: NarrativeRequest):
    if not body.matched_content.strip():
        raise HTTPException(
            status_code=400,
            detail="No matched content provided. Run 'Match to Funder' first.",
        )
    try:
        result = narrative.generate_narrative(
            matched_content=body.matched_content,
            funder_context=body.funder_context,
            section_type=body.section_type,
            word_count=body.word_count,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Narrative generation failed: {str(e)}")
