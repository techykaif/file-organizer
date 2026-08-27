import importlib.metadata
import subprocess
import sys

import pytest

from file_organizer import cli
from file_organizer.organizer import OrganizerSummary


def run_cli_module(*args):
    return subprocess.run(
        [sys.executable, "-m", "file_organizer.cli", *args],
        capture_output=True,
        text=True,
        check=False,
    )


def test_cli_help():
    result = run_cli_module("--help")
    assert result.returncode == 0
    assert "usage: file-organizer" in result.stdout
    assert "--dry-run" in result.stdout
    assert "--recursive" in result.stdout
    assert "--config" in result.stdout
    assert "--yes" in result.stdout


def test_cli_version():
    result = run_cli_module("--version")
    assert result.returncode == 0

    try:
        expected_version = importlib.metadata.version("kaif-file-organizer")
    except importlib.metadata.PackageNotFoundError:
        expected_version = "unknown"

    assert result.stdout.strip() == f"file-organizer {expected_version}"


def test_cli_invalid_path():
    result = run_cli_module("/path/that/does/not/exist/12345", "--yes")
    assert result.returncode == 1
    assert "does not exist" in result.stderr


def test_cli_file_path_rejected(tmp_path):
    target = tmp_path / "file.txt"
    target.write_text("not a directory")

    result = run_cli_module(str(target), "--yes")
    assert result.returncode == 1
    assert "is not a directory" in result.stderr


def test_cli_dry_run(tmp_path):
    (tmp_path / "test.txt").write_text("hello")

    result = run_cli_module(str(tmp_path), "--dry-run")

    assert result.returncode == 0
    assert "--- Dry Run Summary ---" in result.stdout
    assert "Files found:          1" in result.stdout
    assert "Files to move:        1" in result.stdout
    assert (tmp_path / "test.txt").exists()
    assert not (tmp_path / "Documents").exists()


def test_cli_normal_run(tmp_path):
    (tmp_path / "test.txt").write_text("hello")

    result = run_cli_module(str(tmp_path), "--yes")

    assert result.returncode == 0
    assert "--- Organization Summary ---" in result.stdout
    assert "Files moved:          1" in result.stdout
    assert not (tmp_path / "test.txt").exists()
    assert (tmp_path / "Documents" / "test.txt").exists()


def test_cli_recursive(tmp_path):
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "test.jpg").write_text("image")

    result = run_cli_module(str(tmp_path), "--yes", "--recursive")

    assert result.returncode == 0
    assert "Files found:          1" in result.stdout
    assert "Files moved:          1" in result.stdout
    assert (tmp_path / "Images" / "test.jpg").exists()
    assert not (sub / "test.jpg").exists()


def test_cli_custom_config(tmp_path):
    (tmp_path / "data.csv").write_text("1,2,3")
    config_file = tmp_path / "config.json"
    config_file.write_text('{"Data": [".csv"]}')

    result = run_cli_module(str(tmp_path), "--yes", "--config", str(config_file))

    assert result.returncode == 0
    assert (tmp_path / "Data" / "data.csv").exists()


def test_cli_invalid_config_json(tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text("invalid json")

    result = run_cli_module(str(tmp_path), "--yes", "--config", str(config_file))

    assert result.returncode == 1
    assert "Error loading configuration" in result.stderr
    assert "Invalid JSON in config file" in result.stderr


def test_cli_config_must_be_object(tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text("[]")

    result = run_cli_module(str(tmp_path), "--yes", "--config", str(config_file))

    assert result.returncode == 1
    assert "Configuration must be a JSON object" in result.stderr


def test_cli_missing_config(tmp_path):
    result = run_cli_module(
        str(tmp_path), "--yes", "--config", str(tmp_path / "missing.json")
    )

    assert result.returncode == 1
    assert "Configuration file not found" in result.stderr


def test_cli_main_confirmation_declined(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(sys, "argv", ["file-organizer", str(tmp_path)])
    monkeypatch.setattr("builtins.input", lambda _: "n")

    with pytest.raises(SystemExit) as exc_info:
        cli.main()

    assert exc_info.value.code == 0
    assert "Operation cancelled." in capsys.readouterr().out


def test_cli_main_summary_and_success(monkeypatch, tmp_path, capsys):
    class FakeOrganizer:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

        def run(self):
            return OrganizerSummary(
                found=3, moved=2, duplicates_skipped=1, collisions_handled=1
            )

    monkeypatch.setattr(cli, "FileOrganizer", FakeOrganizer)
    monkeypatch.setattr(sys, "argv", ["file-organizer", str(tmp_path), "--yes"])

    with pytest.raises(SystemExit) as exc_info:
        cli.main()

    output = capsys.readouterr().out
    assert exc_info.value.code == 0
    assert "Files found:          3" in output
    assert "Files moved:          2" in output
    assert "Duplicates skipped:   1" in output
    assert "Collisions handled:   1" in output


def test_cli_main_dry_run_summary(monkeypatch, tmp_path, capsys):
    class FakeOrganizer:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

        def run(self):
            return OrganizerSummary(
                found=4, moved=4, duplicates_skipped=1, collisions_handled=2
            )

    monkeypatch.setattr(cli, "FileOrganizer", FakeOrganizer)
    monkeypatch.setattr(
        sys, "argv", ["file-organizer", str(tmp_path), "--dry-run"]
    )

    with pytest.raises(SystemExit) as exc_info:
        cli.main()

    output = capsys.readouterr().out
    assert exc_info.value.code == 0
    assert "--- Dry Run Summary ---" in output
    assert "Duplicates to skip:   1" in output
    assert "Collisions to handle: 2" in output


def test_cli_main_reports_errors(monkeypatch, tmp_path, capsys):
    class FakeOrganizer:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

        def run(self):
            return OrganizerSummary(found=1, moved=0, errors=1)

    monkeypatch.setattr(cli, "FileOrganizer", FakeOrganizer)
    monkeypatch.setattr(sys, "argv", ["file-organizer", str(tmp_path), "--yes"])

    with pytest.raises(SystemExit) as exc_info:
        cli.main()

    output = capsys.readouterr().out
    assert exc_info.value.code == 1
    assert "Errors encountered:   1" in output


def test_cli_main_dry_run_reports_errors(monkeypatch, tmp_path, capsys):
    class FakeOrganizer:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

        def run(self):
            return OrganizerSummary(found=1, moved=0, errors=1)

    monkeypatch.setattr(cli, "FileOrganizer", FakeOrganizer)
    monkeypatch.setattr(
        sys, "argv", ["file-organizer", str(tmp_path), "--dry-run"]
    )

    with pytest.raises(SystemExit) as exc_info:
        cli.main()

    output = capsys.readouterr().out
    assert exc_info.value.code == 1
    assert "Errors encountered:   1" in output


def test_cli_argument_parsing(monkeypatch, tmp_path):
    captured = {}

    class FakeOrganizer:
        def __init__(self, **kwargs):
            captured.update(kwargs)

        def run(self):
            return OrganizerSummary()

    monkeypatch.setattr(cli, "FileOrganizer", FakeOrganizer)
    monkeypatch.setattr(
        sys,
        "argv",
        ["file-organizer", str(tmp_path), "--yes", "--dry-run", "--recursive"],
    )

    with pytest.raises(SystemExit) as exc_info:
        cli.main()

    assert exc_info.value.code == 0
    assert captured == {
        "target_dir": tmp_path.resolve(),
        "categories": None,
        "dry_run": True,
        "recursive": True,
    }
