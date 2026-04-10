from pydantic import BaseModel
from typing import List, Optional


class OrgProfile(BaseModel):
    mission: str = ""
    geographic_reach: str = ""
    history: str = ""
    leadership: str = ""


class Program(BaseModel):
    name: str
    description: str = ""
    outcomes: str = ""
    population: str = ""


class ProgramUpdate(BaseModel):
    name: str
    description: str = ""
    outcomes: str = ""
    population: str = ""


class Stat(BaseModel):
    label: str
    value: str


class SaveMemoryRequest(BaseModel):
    profile: OrgProfile
    stats: List[Stat] = []


class FunderMatchRequest(BaseModel):
    funder_priorities: str


class NarrativeRequest(BaseModel):
    matched_content: str
    funder_context: str
    section_type: str = "Organization Background"
    word_count: int = 300
