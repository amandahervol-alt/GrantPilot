import json
import re
from core.matching import call_anthropic_matching
from core.memory import get_org_memory

def execute(funder_priorities: str) -> list:
    """
    Executes Workflow A: Funder Matching.
    Retrieves org memory, calls Anthropic API, and parses the returned JSON matches.
    """
    org_data = get_org_memory()
    if not org_data:
        raise ValueError("No organizational data found. Please save organization data first.")

    raw_response = call_anthropic_matching(org_data, funder_priorities)
    
    try:
        # Regex to locate JSON object or array even if conversational text is present
        match = re.search(r'(\{[\s\S]*\})', raw_response)
        if match:
            json_str = match.group(1)
        else:
            # Fallback to stripped string
            json_str = raw_response.strip()
            
        data = json.loads(json_str)
        matches = data.get("matches", [])
        return matches
    except (json.JSONDecodeError, AttributeError) as e:
        print(f"Failed to parse Claude response: {raw_response}")
        raise ValueError("The AI response could not be parsed as structured JSON. Please retry.")

if __name__ == "__main__":
    # Test stub
    test_priorities = "We fund after-school STEM education and underserved youth mentorship."
    try:
        results = execute(test_priorities)
        print(f"Match Results: {results}")
    except Exception as e:
        print(f"Error: {e}")
