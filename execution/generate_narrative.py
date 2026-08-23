from typing import Dict, List, Optional
from core.narrative import generate_grant_narrative

def execute(
    section_type: str,
    target_word_count: int = 400,
    funder_context: str = "",
    matched_points: Optional[List[str]] = None
) -> Dict:
    """
    Executes Workflow B: Generate Narrative Draft.
    Orchestrates retrieval of org memory + documents and passes structured parameters to AI.
    """
    return generate_grant_narrative(
        section_type=section_type,
        target_word_count=target_word_count,
        funder_context=funder_context,
        matched_points=matched_points
    )

if __name__ == "__main__":
    # Test execution stub
    try:
        draft_res = execute(
            section_type="Statement of Need",
            target_word_count=250,
            funder_context="Supporting early literacy initiatives"
        )
        print(f"Generated draft: {draft_res['draft'][:200]}...")
    except Exception as e:
        print(f"Error during narrative generation: {e}")
