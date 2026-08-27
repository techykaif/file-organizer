import json
import subprocess
import sys

import pytest

from file_organizer import cli
from file_organizer.organizer import OrganizationSummary


def run_cli(monkeypatch, args):
    monkeypatch.setattr(sys, "argv", ["file-organizer", *args])
    cli.main()


def test_cli_help(monkeypatch, capsys):
    run_cli(monkeypatch, ["--help"])
    assert "usage:" in capsys.readouterr().out


def test_cli_version(monkeypatch, capsys):
    run_cli(monkeypatch, ["--version"])
    assert capsys.readouterr().out.strip() == cli.__version__


def test_cli_dry_run(monkeypatch, tmp_path, capsys):
    (tmp_path / "test.txt").write_text("hello")
    run_cli(monkeypatch, [str(tmp_path), "--dry-run"])
    output = capsys.readouterr().out
    assert "Dry run" in output
    assert (tmp_path / "test.txt").exists()


def test_cli_yes_moves_file(monkeypatch, tmp_path, capsys):
    (tmp_path / "test.txt").write_text("hello")
    run_cli(monkeypatch, [str(tmp_path), "--yes"])
    output = capsys.readouterr().out
    assert "Organization Summary" in output
    assert "Files moved:          1" in output
    assert (tmp_path / "Documents" / "test.txt").exists()


def test_cli_main_config_and_recursive(monkeypatch, tmp_path, capsys):
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "data.csv").write_text("1,2")
    config = tmp_path / "config.json"
    config.write_text('{"Data": [".csv"]}')

    run_cli(
        monkeypatch,
        [str(tmp_path), "--yes", "--recursive", "--config", str(config)],
    )
    assert (tmp_path / "Data" / "data.csv").exists()
    assert "Files moved:" in capsys.readouterr().out


def test_cli_main_reports_errors(monkeypatch, tmp_path, capsys):
    class FakeSummary:
        files_moved = 0
        files_skipped = 0
        duplicates = 0
        errors = 1

    def fake_organize(*args, **kwargs):
        print("permission denied", file=sys.stderr)
        return FakeSummary()

    monkeypatch.setattr(cli, "organize_directory", fake_organize)
    run_cli(monkeypatch, [str(tmp_path), "--yes"])
    assert "Errors:            1" in capsys.readouterr().out


def test_cli_invalid_path(monkeypatch, tmp_path, capsys):
    run_cli(monkeypatch, [str(tmp_path / "missing")])
    assert "does not exist" in capsys.readouterr().err


def test_cli_config_error(monkeypatch, tmp_path, capsys):
    config = tmp_path / "bad.json"
    config.write_text("[]")
    run_cli(monkeypatch, [str(tmp_path), "--config", str(config)])
    assert "Configuration must be a JSON object" in capsys.readouterr().err


def test_cli_keyboard_interrupt(monkeypatch, tmp_path, capsys):
    def fake_organize(*args, **kwargs):
        raise KeyboardInterrupt

    monkeypatch.setattr(cli, "organize_directory", fake_organize)
    run_cli(monkeypatch, [str(tmp_path), "--yes"])
    assert "Operation cancelled" in capsys.readouterr().err


def test_cli_permission_error(monkeypatch, tmp_path, capsys):
    def fake_organize(*args, **kwargs):
        raise PermissionError("no access")

    monkeypatch.setattr(cli, "organize_directory", fake_organize)
    run_cli(monkeypatch, [str(tmp_path), "--yes"])
    assert "Permission denied" in capsys.readouterr().err


def test_cli_os_error(monkeypatch, tmp_path, capsys):
    def fake_organize(*args, **kwargs):
        raise OSError("disk error")

    monkeypatch.setattr(cli, "organize_directory", fake_organize)
    run_cli(monkeypatch, [str(tmp_path), "--yes"])
    assert "Operation failed" in capsys.readouterr().err


def test_cli_confirmation_declined(monkeypatch, tmp_path, capsys):
    (tmp_path / "test.txt").write_text("hello")
    monkeypatch.setattr(cli, "confirm", lambda *args, **kwargs: False)
    run_cli(monkeypatch, [str(tmp_path)])
    assert "Cancelled" in capsys.readouterr().out


def test_cli_summary_fields(monkeypatch, tmp_path, capsys):
    summary = OrganizationSummary(files_moved=2, files_skipped=3, duplicates=1, errors=4)

    def fake_organize(*args, **kwargs):
        return summary

    monkeypatch.setattr(cli, "organize_directory", fake_organize)
    run_cli(monkeypatch, [str(tmp_path), "--yes"])
    output = capsys.readouterr().out
    assert "Files moved:" in output
    assert "Files skipped:" in output
    assert "Duplicates:" in output
    assert "Errors:" in output


def test_cli_json_config(monkeypatch, tmp_path, capsys):
    config = tmp_path / "config.json"
    config.write_text(json.dumps({"Images": [".png"]}))
    (tmp_path / "image.png").write_text("image")
    run_cli(monkeypatch, [str(tmp_path), "--yes", "--config", str(config)])
    assert (tmp_path / "Images" / "image.png").exists()
    assert "Files moved:" in capsys.readouterr().out


def test_cli_recursive_disabled(monkeypatch, tmp_path, capsys):
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "data.csv").write_text("1,2")
    run_cli(monkeypatch, [str(tmp_path), "--yes"])
    assert (sub / "data.csv").exists()
    assert "Files moved:" in capsys.readouterr().out


def test_cli_verbose(monkeypatch, tmp_path, capsys):
    (tmp_path / "test.txt").write_text("hello")
    run_cli(monkeypatch, [str(tmp_path), "--yes", "--verbose"])
    assert "Organization Summary" in capsys.readouterr().out


def test_cli_empty_directory(monkeypatch, tmp_path, capsys):
    run_cli(monkeypatch, [str(tmp_path), "--yes"])
    output = capsys.readouterr().out
    assert "Files moved:" in output


def test_cli_existing_destination(monkeypatch, tmp_path, capsys):
    (tmp_path / "test.txt").write_text("source")
    destination = tmp_path / "Documents"
    destination.mkdir()
    (destination / "test.txt").write_text("existing")
    run_cli(monkeypatch, [str(tmp_path), "--yes"])
    assert "Duplicates:" in capsys.readouterr().out


def test_cli_invalid_config_path(monkeypatch, tmp_path, capsys):
    run_cli(monkeypatch, [str(tmp_path), "--config", str(tmp_path / "missing.json")])
    assert "Configuration file not found" in capsys.readouterr().err


def test_cli_help_contains_options(monkeypatch, capsys):
    with pytest.raises(SystemExit) as exc_info:
        run_cli(monkeypatch, ["--help"])
    assert exc_info.value.code == 0
    output = capsys.readouterr().out
    assert "--recursive" in output
    assert "--dry-run" in output
    assert "--config" in output
