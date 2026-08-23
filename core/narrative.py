import os
import re
from typing import Dict, List, Optional
from anthropic import Anthropic, APIError, AuthenticationError
from dotenv import load_dotenv
from core.memory import get_org_memory
from core.documents import get_combined_document_text

load_dotenv()

def generate_grant_narrative(
    section_type: str,
    target_word_count: int = 400,
    funder_context: str = "",
    matched_points: Optional[List[str]] = None
) -> Dict:
    """
    Generates a section-specific grant narrative grounded strictly in organizational memory
    and indexed document excerpts.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or api_key.strip() == "your_anthropic_api_key_here":
        raise ValueError("ANTHROPIC_API_KEY is missing or invalid in your .env file. Please set a valid Anthropic API key.")

    model_name = os.getenv("ANTHROPIC_MODEL", "claude-3-7-sonnet-20250219")
    client = Anthropic(api_key=api_key)

    # 1. Retrieve Org Context
    org_data = get_org_memory()
    org_context = "Organizational Data:\n"
    for key, value in org_data.items():
        if value and str(value).strip():
            org_context += f"--- {key.upper()} ---\n{value}\n\n"

    doc_context = get_combined_document_text(max_chars=8000)
    if doc_context:
        org_context += f"\n--- SUPPORTING DOCUMENTS ---\n{doc_context}\n"

    # 2. Build Matched Highlights
    matched_text = ""
    if matched_points:
        matched_text = "\nPrioritized Highlights / Matched Points:\n" + "\n".join(f"- {p}" for p in matched_points)

    system_prompt = (
        "You are GrantPilot, an expert AI grant narrative writer for nonprofits. "
        "Your task is to draft a compelling, professional, copy-paste ready grant narrative section.\n\n"
        "CRITICAL RULES:\n"
        "1. STRICT ANTI-HALLUCINATION: Rely ONLY on the provided organizational data, documents, and matched highlights. "
        "NEVER invent statistics, partners, staff names, past awards, or impact numbers.\n"
        "2. FLAG GAPS: If critical information needed for this section is missing from the provided data, insert a clear visual flag formatted as: "
        "`[GAP: description of missing data needed, e.g. Specific local poverty percentage]`. Do NOT make up numbers to fill gaps.\n"
        f"3. WORD COUNT TARGET: Aim for approximately {target_word_count} words (+/- 10%). Maintain complete thoughts and professional flow.\n"
        "4. STYLE: Persuasive, clear, mission-driven, and tailored to grant evaluation rubrics.\n"
        "5. Output clean Markdown ready for copy-pasting."
    )

    user_prompt = (
        f"SECTION TYPE TO DRAFT: {section_type}\n"
        f"TARGET WORD COUNT: ~{target_word_count} words\n"
        f"FUNDER CONTEXT / PRIORITIES:\n{funder_context or 'General Grant Proposal'}\n\n"
        f"{org_context}\n"
        f"{matched_text}\n\n"
        f"Please write the draft for '{section_type}' following all constraints."
    )

    try:
        response = client.messages.create(
            model=model_name,
            max_tokens=3000,
            temperature=0.3,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )
        draft_text = response.content[0].text.strip()
        
        # Extract flagged gaps using regex
        gaps = re.findall(r'\[GAP:\s*(.*?)\]', draft_text, re.IGNORECASE)
        actual_word_count = len(draft_text.split())

        return {
            "section_type": section_type,
            "target_word_count": target_word_count,
            "actual_word_count": actual_word_count,
            "draft": draft_text,
            "gaps": gaps
        }
    except AuthenticationError:
        raise ValueError("Anthropic Authentication failed: Your ANTHROPIC_API_KEY is invalid or expired.")
    except APIError as e:
        raise ValueError(f"Anthropic API error: {e.message}")
    except Exception as e:
        raise ValueError(f"Error generating narrative: {str(e)}")
