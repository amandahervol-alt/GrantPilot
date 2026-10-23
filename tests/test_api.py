"""End-to-end tests for the FastAPI routes (storage isolated, Anthropic mocked)."""


def test_root_serves_ui(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "GrantPilot" in response.text


def test_org_load_returns_defaults_when_empty(client):
    response = client.get("/api/org/load")
    assert response.status_code == 200
    assert response.json() == {
        "mission": "",
        "programs": "",
        "outcomes": "",
        "stats": "",
    }


def test_org_save_then_load_round_trip(client):
    payload = {
        "mission": "Advance nonprofit grant readiness.",
        "programs": "Grant writing workshops",
        "outcomes": "30 funded proposals",
        "stats": "8 staff",
    }
    save = client.post("/api/org/save", json=payload)
    assert save.status_code == 200
    assert save.json()["status"] == "success"

    load = client.get("/api/org/load")
    assert load.status_code == 200
    body = load.json()
    assert body["mission"] == "Advance nonprofit grant readiness."
    assert body["stats"] == "8 staff"


def test_document_upload_txt(client):
    content = b"GrantPilot was established in 2024 to help nonprofits."
    response = client.post(
        "/api/documents/upload",
        files={"file": ("overview.txt", content, "text/plain")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["document"]["filename"] == "overview.txt"
    assert body["document"]["word_count"] == 8

    listing = client.get("/api/documents")
    assert any(
        d["filename"] == "overview.txt" for d in listing.json()["documents"]
    )


def test_document_upload_unsupported_type(client):
    response = client.post(
        "/api/documents/upload",
        files={"file": ("payload.zip", b"PK\x05\x06", "application/zip")},
    )
    assert response.status_code == 400
    assert "Unsupported file format" in response.json()["detail"]


def test_document_upload_empty_file(client):
    response = client.post(
        "/api/documents/upload",
        files={"file": ("empty.txt", b"", "text/plain")},
    )
    assert response.status_code == 400


def test_document_delete_unknown_id(client):
    response = client.delete("/api/documents/does-not-exist")
    assert response.status_code == 404
    assert response.json()["detail"] == "Document not found."


def test_funder_match_endpoint(client, api_key, fake_anthropic):
    client.post(
        "/api/org/save",
        json={
            "mission": "Support historic preservation.",
            "programs": "Restoration grants",
            "outcomes": "5 buildings restored",
            "stats": "3 staff",
        },
    )
    fake_anthropic.next_text = (
        '{"matches": [{"content": "Restored 5 historic buildings", '
        '"explanation": "Directly aligned with preservation funding.", "rank": 1}]}'
    )
    response = client.post(
        "/api/funder/match",
        json={"funder_priorities": "We fund historic preservation projects."},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["matches"][0]["content"] == "Restored 5 historic buildings"
    assert body["matches"][0]["rank"] == 1


def test_funder_match_requires_org_data(client):
    # No org memory saved yet in this isolated data dir.
    response = client.post(
        "/api/funder/match",
        json={"funder_priorities": "We fund STEM education."},
    )
    assert response.status_code == 400
    assert "No organizational data found" in response.json()["detail"]


def test_narrative_generate_endpoint(client, api_key, fake_anthropic):
    fake_anthropic.next_text = (
        "The program will serve 200 youth. [GAP: youth population baseline]"
    )
    response = client.post(
        "/api/narrative/generate",
        json={
            "section_type": "Program Description",
            "target_word_count": 300,
            "funder_context": "Focus on underserved youth.",
            "matched_points": ["After-school STEM program"],
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["section_type"] == "Program Description"
    assert body["gaps"] == ["youth population baseline"]
    assert "200 youth" in body["draft"]


def test_narrative_generate_rejects_out_of_range_word_count(client):
    response = client.post(
        "/api/narrative/generate",
        json={
            "section_type": "Executive Summary",
            "target_word_count": 5000,  # above the 50-2000 validation range
        },
    )
    assert response.status_code == 422


def test_narrative_generate_requires_api_key(client, fake_anthropic, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    response = client.post(
        "/api/narrative/generate",
        json={
            "section_type": "Executive Summary",
            "target_word_count": 300,
        },
    )
    assert response.status_code == 400
    assert "ANTHROPIC_API_KEY" in response.json()["detail"]
