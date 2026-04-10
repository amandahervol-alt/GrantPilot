import os
import anthropic

MODEL = "claude-sonnet-4-5"

_client = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


def generate_narrative(
    matched_content: str,
    funder_context: str,
    section_type: str,
    word_count: int,
) -> dict:
    prompt = f"""You are GrantPilot, an expert grant writer.

Write a "{section_type}" section for a grant proposal.

MATCHED ORGANIZATIONAL CONTENT (your only source material):
{matched_content}

FUNDER CONTEXT / PRIORITIES:
{funder_context}

Instructions:
1. Write approximately {word_count} words.
2. Every claim, statistic, and program reference must come directly from the matched content above.
3. Do not invent statistics, outcomes, or programs. If you need a specific detail that isn't in the source material, write [NEEDS DATA: describe what's missing] inline.
4. Write in a compelling, professional grant writing style — clear, specific, and funder-focused.
5. The output should be copy-paste ready. Do not include headings, preamble, or commentary — just the narrative text."""

    response = _get_client().messages.create(
        model=MODEL,
        max_tokens=3000,
        system=(
            "You are GrantPilot, a grant writing assistant. Write compelling, accurate "
            "grant narratives grounded strictly in the organizational data provided. "
            "Never fabricate statistics or programs."
        ),
        messages=[{"role": "user", "content": prompt}],
    )

    return {"narrative": response.content[0].text}
