from fastapi import APIRouter, HTTPException, UploadFile, File
from api.models import (
    OrgDataRequest,
    FunderMatchRequest,
    FunderMatchResponse,
    NarrativeRequest,
    NarrativeResponse,
    DocumentListResponse
)
from core.memory import get_org_memory
import execution.save_org_data as save_org_data
import execution.match_funder as match_funder
import execution.parse_document as parse_document
import execution.generate_narrative as generate_narrative

router = APIRouter()

# --- Org Memory Endpoints ---

@router.get("/org/load")
async def load_org_data_endpoint():
    """Loads existing organizational data from storage."""
    try:
        data = get_org_memory()
        return data or {"mission": "", "programs": "", "outcomes": "", "stats": ""}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load org memory: {str(e)}")

@router.post("/org/save")
async def save_org_data_endpoint(request: OrgDataRequest):
    """Saves organizational memory to local file."""
    try:
        success = save_org_data.execute(request.model_dump())
        if success:
            return {"status": "success", "message": "Organizational data saved successfully."}
        else:
            raise HTTPException(status_code=500, detail="Failed to write organizational data.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Document Ingestion Endpoints ---

@router.get("/documents", response_model=DocumentListResponse)
async def list_documents_endpoint():
    """Lists all parsed and indexed documents."""
    try:
        docs = parse_document.list_indexed_documents()
        # Exclude raw content from list response for speed
        sanitized = [
            {
                "id": d["id"],
                "filename": d["filename"],
                "uploaded_at": d["uploaded_at"],
                "word_count": d.get("word_count", 0),
                "char_count": d.get("char_count", 0)
            }
            for d in docs
        ]
        return {"documents": sanitized}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve documents: {str(e)}")

@router.post("/documents/upload")
async def upload_document_endpoint(file: UploadFile = File(...)):
    """Uploads, parses, and indexes a PDF, DOCX, or TXT document."""
    try:
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")
        
        doc_record = parse_document.execute(file.filename, contents)
        return {
            "status": "success",
            "message": f"Successfully indexed '{file.filename}' ({doc_record['word_count']} words).",
            "document": {
                "id": doc_record["id"],
                "filename": doc_record["filename"],
                "uploaded_at": doc_record["uploaded_at"],
                "word_count": doc_record["word_count"]
            }
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing document: {str(e)}")

@router.delete("/documents/{doc_id}")
async def delete_document_endpoint(doc_id: str):
    """Deletes an indexed document."""
    try:
        success = parse_document.remove_document(doc_id)
        if success:
            return {"status": "success", "message": "Document removed from index."}
        else:
            raise HTTPException(status_code=404, detail="Document not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- AI Orchestration Endpoints ---

@router.post("/funder/match", response_model=FunderMatchResponse)
async def match_funder_endpoint(request: FunderMatchRequest):
    """Matches organizational memory and documents against funder priorities."""
    try:
        matches = match_funder.execute(request.funder_priorities)
        return {"matches": matches}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Funder matching failed: {str(e)}")

@router.post("/narrative/generate", response_model=NarrativeResponse)
async def generate_narrative_endpoint(request: NarrativeRequest):
    """Generates a grant narrative section grounded in org memory and documents."""
    try:
        result = generate_narrative.execute(
            section_type=request.section_type,
            target_word_count=request.target_word_count,
            funder_context=request.funder_context,
            matched_points=request.matched_points
        )
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Narrative generation failed: {str(e)}")
