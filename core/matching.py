from anthropic import Anthropic, APIError, AuthenticationError
import os
from dotenv import load_dotenv
from core.documents import get_combined_document_text

load_dotenv()

def call_anthropic_matching(org_data: dict, funder_priorities: str) -> str:
    """Calls the Anthropic API to match org data and indexed documents with funder priorities."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or api_key.strip() == "your_anthropic_api_key_here":
        raise ValueError("ANTHROPIC_API_KEY is missing or invalid in your .env file. Please set a valid Anthropic API key.")

    model_name = os.getenv("ANTHROPIC_MODEL", "claude-3-7-sonnet-20250219")
    client = Anthropic(api_key=api_key)

    # Build context from org memory
    org_context = "Organizational Data:\n"
    for key, value in org_data.items():
        if value and str(value).strip():
            org_context += f"--- {key.upper()} ---\n{value}\n\n"

    # Add indexed documents if available
    doc_context = get_combined_document_text(max_chars=12000)
    if doc_context:
        org_context += f"\n--- SUPPORTING UPLOADED DOCUMENTS ---\n{doc_context}\n"

    system_prompt = (
        "You are GrantPilot, an AI grant writing assistant for nonprofits. "
        "Your task is to analyze the provided organizational data and supporting documents against the funder's priority areas.\n"
        "1. Identify key overlaps and relevant content.\n"
        "2. Provide a ranked list of relevant content points.\n"
        "3. Provide a clear explanation for why each piece fits the funder's stated priorities.\n"
        "IMPORTANT: Work ONLY from the provided org data and documents. Do not hallucinate or invent metrics, programs, or outcomes. "
        "If gaps exist or no relevant data is found for a priority, explicitly flag it.\n"
        "Respond ONLY with a valid JSON object following this schema:\n"
        '{"matches": [{"content": "string", "explanation": "string", "rank": number}]}'
    )

    user_prompt = (
        f"{org_context}\n"
        f"Funder Priority Areas:\n{funder_priorities}"
    )

    try:
        response = client.messages.create(
            model=model_name,
            max_tokens=2048,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )
        return response.content[0].text
    except AuthenticationError:
        raise ValueError("Anthropic Authentication failed: Your ANTHROPIC_API_KEY is invalid or expired.")
    except APIError as e:
        raise ValueError(f"Anthropic API error: {e.message}")
    except Exception as e:
        raise ValueError(f"Error communicating with AI service: {str(e)}")
