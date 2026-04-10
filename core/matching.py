import os
import anthropic
from .memory import get_all_memory
from .documents import get_all_document_text

MODEL = "claude-sonnet-4-5"

_client = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


def _build_org_context(memory: dict, documents: list) -> str:
    lines = []
    profile = memory.get("profile", {})

    if profile.get("mission"):
        lines.append(f"MISSION:\n{profile['mission']}")
    if profile.get("geographic_reach"):
        lines.append(f"GEOGRAPHIC REACH:\n{profile['geographic_reach']}")
    if profile.get("history"):
        lines.append(f"ORGANIZATIONAL HISTORY:\n{profile['history']}")
    if profile.get("leadership"):
        lines.append(f"LEADERSHIP CAPACITY:\n{profile['leadership']}")

    programs = memory.get("programs", [])
    if programs:
        lines.append("PROGRAMS:")
        for p in programs:
            block = [f"  Program: {p['name']}"]
            if p.get("description"):
                block.append(f"  Description: {p['description']}")
            if p.get("outcomes"):
                block.append(f"  Outcomes: {p['outcomes']}")
            if p.get("population"):
                block.append(f"  Population served: {p['population']}")
            lines.append("\n".join(block))

    stats = memory.get("stats", [])
    if stats:
        lines.append("IMPACT STATISTICS:")
        for s in stats:
            lines.append(f"  - {s['label']}: {s['value']}")

    if documents:
        lines.append("UPLOADED DOCUMENTS:")
        for doc in documents:
            # Cap each document at 4000 chars to stay within context limits
            text = doc["content"]
            truncated = text[:4000] + "\n...[truncated]" if len(text) > 4000 else text
            lines.append(f"\n[Document: {doc['filename']}]\n{truncated}")

    return "\n\n".join(lines)


def match_to_funder(funder_priorities: str) -> dict:
    memory = get_all_memory()
    documents = get_all_document_text()
    org_context = _build_org_context(memory, documents)

    if not org_context.strip():
        return {
            "error": "No organizational data found. Please add your organization's "
                     "information in the 'Your Organization' tab first."
        }

    prompt = f"""You are GrantPilot, an expert grant writing assistant.

ORGANIZATION DATA:
{org_context}

FUNDER PRIORITY AREAS:
{funder_priorities}

Your task:
1. Review the organization's data carefully.
2. Identify the 3–7 most relevant pieces of content (programs, stats, outcomes, history, leadership) that align with the funder's priorities.
3. Rank them from most to least relevant.
4. For each match, explain in 1–2 sentences exactly why it connects to this funder's priorities.
5. Only include content that is genuinely present in the organization data — do not invent or embellish.

Format each match as:
**[Rank]. [Content title]**
Content: [the specific data, stat, or program description]
Why it's relevant: [your explanation]

End with a brief **Gaps to Address** section listing any funder priorities that don't have strong matching content in the org data."""

    response = _get_client().messages.create(
        model=MODEL,
        max_tokens=2000,
        system=(
            "You are GrantPilot, a grant writing assistant. Help nonprofits identify "
            "which parts of their organizational data are most relevant to a specific "
            "funder's priorities. Be precise and grounded only in the data provided."
        ),
        messages=[{"role": "user", "content": prompt}],
    )

    return {"matches": response.content[0].text}
