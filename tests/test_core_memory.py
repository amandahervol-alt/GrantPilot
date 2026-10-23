"""Unit tests for core.memory — organizational memory load/save."""
import core.memory
from core.memory import get_org_memory, save_org_memory


def test_load_returns_empty_dict_when_file_missing(data_dir):
    assert get_org_memory() == {}


def test_load_parses_valid_json(data_dir):
    data = {"mission": "Help people.", "programs": "Education"}
    data_dir.joinpath("org_memory.json").write_text(
        __import__("json").dumps(data)
    )
    assert get_org_memory() == data


def test_load_returns_empty_dict_on_corrupt_json(data_dir):
    data_dir.joinpath("org_memory.json").write_text("{not valid json")
    assert get_org_memory() == {}


def test_save_writes_valid_json(data_dir):
    data = {"mission": "Save the bay.", "stats": "12 staff"}
    assert save_org_memory(data) is True
    on_disk = __import__("json").loads(
        data_dir.joinpath("org_memory.json").read_text()
    )
    assert on_disk == data


def test_save_then_load_round_trip(data_dir):
    data = {"mission": "Round trip.", "outcomes": "Trained 40 teachers."}
    save_org_memory(data)
    assert get_org_memory() == data
