"""Unit tests for core.narrative and execution workflows (Anthropic mocked)."""
import pytest

import execution.generate_narrative
import execution.match_funder
from core.narrative import generate_grant_narrative


# ---------------------------------------------------------------- narrative


def test_narrative_missing_api_key_rejected(monkeypatch, data_dir):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
        generate_grant_narrative("Executive Summary", 200)


def test_narrative_placeholder_api_key_rejected(monkeypatch, data_dir):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "your_anthropic_api_key_here")
    with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
        generate_grant_narrative("Executive Summary", 200)


def test_narrative_happy_path(api_key, fake_anthropic, data_dir):
    fake_anthropic.next_text = (
        "Draft narrative text. [GAP: local poverty rate] More text. "
        "[GAP: baseline literacy score] End of draft."
    )
    result = generate_grant_narrative("Program Description", target_word_count=300)
    assert result["section_type"] == "Program Description"
    assert result["target_word_count"] == 300
    assert result["draft"] == fake_anthropic.next_text
    # Gaps flagged with the [GAP: ...] marker are surfaced in the result.
    assert result["gaps"] == ["local poverty rate", "baseline literacy score"]
    assert result["actual_word_count"] == len(fake_anthropic.next_text.split())
    # The request carried the section type and the system rules.
    kwargs = fake_anthropic.last_messages.captured_kwargs
    assert "Program Description" in kwargs["messages"][0]["content"]
    assert kwargs["system"].startswith("You are GrantPilot")


def test_narrative_wraps_anthropic_errors(api_key, fake_anthropic, data_dir):
    # A transport-level failure surfaces as ValueError, not a raw exception.
    import core.narrative

    original = core.narrative.Anthropic

    class Failing:
        def __init__(self, *a, **k):
            class FailingMessages:
                def create(self, **kwargs):
                    raise RuntimeError("simulated transport failure")

            self.messages = FailingMessages()

    core.narrative.Anthropic = Failing
    try:
        with pytest.raises(ValueError, match="Error generating narrative"):
            generate_grant_narrative("Executive Summary", 200)
    finally:
        core.narrative.Anthropic = original


# ----------------------------------------------------------------- matching


def test_match_funder_requires_org_data(data_dir):
    with pytest.raises(ValueError, match="No organizational data found"):
        execution.match_funder.execute("We fund STEM education.")


def test_match_funder_parses_fenced_json_response(
    monkeypatch, api_key, fake_anthropic, data_dir
):
    from core import memory

    memory.save_org_memory({"mission": "Support rural museums."})
    fake_anthropic.next_text = (
        'Here are the matches:\n```json\n{"matches": [{"content": '
        '"Our museum digitization program", "explanation": "Directly aligned.", '
        '"rank": 1}]}\n```'
    )
    matches = execution.match_funder.execute(
        "We fund museum digitization projects."
    )
    assert matches[0]["content"] == "Our museum digitization program"
    assert matches[0]["explanation"] == "Directly aligned."
    # The organization's mission is included in the request.
    kwargs = fake_anthropic.last_messages.captured_kwargs
    assert "Support rural museums." in kwargs["messages"][0]["content"]


def test_match_funder_parses_bare_json_object(
    monkeypatch, api_key, fake_anthropic, data_dir
):
    from core import memory

    memory.save_org_memory({"mission": "Support rural museums."})
    fake_anthropic.next_text = (
        '{"matches": [{"content": "Heritage restoration expertise", '
        '"explanation": "Partial fit.", "rank": 2}]}'
    )
    matches = execution.match_funder.execute("We fund heritage projects.")
    assert matches[0]["content"] == "Heritage restoration expertise"


def test_match_funder_rejects_unparseable_response(
    monkeypatch, api_key, fake_anthropic, data_dir
):
    from core import memory

    memory.save_org_memory({"mission": "Support rural museums."})
    fake_anthropic.next_text = "sorry, I cannot help with that request"
    with pytest.raises(ValueError, match="could not be parsed"):
        execution.match_funder.execute("We fund museum projects.")


def test_generate_narrative_workflow_delegates(
    monkeypatch, api_key, fake_anthropic, data_dir
):
    fake_anthropic.next_text = "Draft from the execution module."
    result = execution.generate_narrative.execute(
        section_type="Outcomes",
        target_word_count=150,
        funder_context="Focus on measurable impact.",
        matched_points=["30 teachers trained"],
    )
    assert result["section_type"] == "Outcomes"
    assert result["draft"] == "Draft from the execution module."
    # The funder context flows through to the model request.
    kwargs = fake_anthropic.last_messages.captured_kwargs
    assert "Focus on measurable impact." in kwargs["messages"][0]["content"]
