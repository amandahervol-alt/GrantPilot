from pydantic import BaseModel, Field
from typing import List, Optional

class OrgDataRequest(BaseModel):
    mission: str = ""
    programs: str = ""
    outcomes: str = ""
    stats: str = ""

class FunderMatchRequest(BaseModel):
    funder_priorities: str

class MatchedContent(BaseModel):
    content: str
    explanation: str
    rank: int

class FunderMatchResponse(BaseModel):
    matches: List[MatchedContent]

class NarrativeRequest(BaseModel):
    section_type: str = "Statement of Need"
    target_word_count: int = Field(default=400, ge=50, le=2000)
    funder_context: Optional[str] = ""
    matched_points: Optional[List[str]] = []

class NarrativeResponse(BaseModel):
    section_type: str
    target_word_count: int
    actual_word_count: int
    draft: str
    gaps: List[str] = []

class DocumentItem(BaseModel):
    id: str
    filename: str
    uploaded_at: str
    word_count: int
    char_count: int

class DocumentListResponse(BaseModel):
    documents: List[DocumentItem]
