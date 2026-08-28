import json

import pytest

from file_organizer.config import get_category_for_extension, load_config


def test_load_config_valid(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps({"Data": [".csv", ".json"]}))

    assert load_config(config_path) == {"Data": [".csv", ".json"]}


def test_load_config_missing(tmp_path):
    with pytest.raises(FileNotFoundError, match="Configuration file not found"):
        load_config(tmp_path / "missing.json")


def test_load_config_invalid_json(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text("{not valid json")

    with pytest.raises(ValueError, match="Invalid JSON in config file"):
        load_config(config_path)


def test_load_config_requires_object(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text("[]")

    with pytest.raises(ValueError, match="Configuration must be a JSON object"):
        load_config(config_path)


def test_load_config_rejects_non_list_value(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps({"Data": ".csv"}))

    with pytest.raises(ValueError, match="must contain a list"):
        load_config(config_path)


def test_load_config_rejects_non_string_extension(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps({"Data": [".csv", 123]}))

    with pytest.raises(ValueError, match="must be a non-empty string"):
        load_config(config_path)


def test_load_config_rejects_empty_extension(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps({"Data": [".csv", ""]}))

    with pytest.raises(ValueError, match="must be a non-empty string"):
        load_config(config_path)


def test_load_config_accepts_empty_object(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text("{}")

    assert load_config(config_path) == {}


def test_get_category_for_extension_case_insensitive():
    categories = {"Code": [".PY", ".Js"]}

    assert get_category_for_extension(".py", categories) == "Code"
    assert get_category_for_extension(".JS", categories) == "Code"
    assert get_category_for_extension(".txt", categories) == "Other"
