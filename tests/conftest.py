"""Shared fixtures for the GrantPilot test suite.

All tests run against temporary directories so the repository's real
data/ files and .tmp/uploads are never modified, and the Anthropic API is
always mocked so no test makes a live call.
"""
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

import core.documents
import core.memory
import main


@pytest.fixture
def data_dir(tmp_path, monkeypatch):
    """Point the module-level storage paths at a temporary directory."""
    path = tmp_path / "data"
    path.mkdir()
    monkeypatch.setattr(core.memory, "MEMORY_FILE_PATH", str(path / "org_memory.json"))
    monkeypatch.setattr(core.documents, "DOCUMENTS_FILE_PATH", str(path / "documents.json"))
    monkeypatch.setattr(core.documents, "UPLOAD_DIR", str(tmp_path / "uploads"))
    return path


@pytest.fixture
def client(data_dir):
    """FastAPI test client with isolated storage."""
    return TestClient(main.app)


class FakeMessages:
    """Stands in for client.messages; returns a canned text response."""

    def __init__(self, text):
        self.text = text
        self.captured_kwargs = None

    def create(self, **kwargs):
        self.captured_kwargs = kwargs
        return SimpleNamespace(content=[SimpleNamespace(text=self.text)])


@pytest.fixture
def fake_anthropic(monkeypatch):
    """Patches core.narrative.Anthropic and core.matching.Anthropic.

    Returns a setter the test uses to choose the response text; the
    captured kwargs of the last call are exposed as .captured_kwargs.
    """

    class FakeAnthropic:
        messages = None  # set below per instance

        def __init__(self, api_key=None):
            self.messages = FakeMessages(FakeAnthropic.next_text)
            FakeAnthropic.last_messages = self.messages

    FakeAnthropic.next_text = ""
    FakeAnthropic.last_messages = None

    import core.matching
    import core.narrative

    monkeypatch.setattr(core.narrative, "Anthropic", FakeAnthropic)
    monkeypatch.setattr(core.matching, "Anthropic", FakeAnthropic)
    return FakeAnthropic


@pytest.fixture
def api_key(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-for-ci")
