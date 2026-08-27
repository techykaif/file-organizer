import json

import pytest

from file_organizer.config import get_category_for_extension, load_config


def test_load_config_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError, match="Configuration file not found"):
        load_config(tmp_path / "missing.json")


def test_load_config_requires_object(tmp_path):
    path = tmp_path / "config.json"
    path.write_text(json.dumps([".txt"]))
    with pytest.raises(TypeError, match="Configuration must be a JSON object"):
        load_config(path)


def test_load_config_reads_categories(tmp_path):
    path = tmp_path / "config.json"
    path.write_text(json.dumps({"Text": [".txt"]}))
    assert load_config(path) == {"Text": [".txt"]}


def test_category_matching_is_case_insensitive():
    categories = {"Documents": [".PDF", ".Txt"]}
    assert get_category_for_extension(".pdf", categories) == "Documents"
    assert get_category_for_extension(".TXT", categories) == "Documents"


def test_unknown_extension_returns_other():
    assert get_category_for_extension(".unknown", {"Documents": [".txt"]}) == "Other"
