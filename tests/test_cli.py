import importlib.metadata
import subprocess
import sys

import pytest

from file_organizer import cli


def test_cli_help():
    result = subprocess.run(
        [sys.executable, "-m", "file_organizer.cli", "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "usage: file-organizer" in result.stdout


def test_cli_version():
    result = subprocess.run(
        [sys.executable, "-m", "file_organizer.cli", "--version"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0

    try:
        expected_version = importlib.metadata.version("kaif-file-organizer")
    except importlib.metadata.PackageNotFoundError:
        expected_version = "unknown"

    assert result.stdout.strip() == f"file-organizer {expected_version}"


def test_cli_invalid_path():
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "file_organizer.cli",
            "/path/that/does/not/exist/12345",
            "--yes",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1
    assert "does not exist" in result.stderr


def test_cli_dry_run(tmp_path):
    (tmp_path / "test.txt").write_text("hello")
    result = subprocess.run(
        [sys.executable, "-m", "file_organizer.cli", str(tmp_path), "--dry-run"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "Files to move:        1" in result.stdout
    assert (tmp_path / "test.txt").exists()
    assert not (tmp_path / "Documents").exists()


def test_cli_normal_run(tmp_path):
    (tmp_path / "test.txt").write_text("hello")
    result = subprocess.run(
        [sys.executable, "-m", "file_organizer.cli", str(tmp_path), "--yes"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "Files moved:          1" in result.stdout
    assert not (tmp_path / "test.txt").exists()
    assert (tmp_path / "Documents" / "test.txt").exists()


def test_cli_recursive(tmp_path):
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "test.jpg").write_text("image")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "file_organizer.cli",
            str(tmp_path),
            "--yes",
            "--recursive",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "Files moved:          1" in result.stdout
    assert (tmp_path / "Images" / "test.jpg").exists()
    assert not (sub / "test.jpg").exists()


def test_cli_custom_config(tmp_path):
    (tmp_path / "data.csv").write_text("1,2,3")
    config_file = tmp_path / "config.json"
    config_file.write_text('{"Data": [".csv"]}')

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "file_organizer.cli",
            str(tmp_path),
            "--yes",
            "--config",
            str(config_file),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "Files moved:          2" in result.stdout
    assert (tmp_path / "Data" / "data.csv").exists()


def test_cli_invalid_config(tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text("invalid json")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "file_organizer.cli",
            str(tmp_path),
            "--yes",
            "--config",
            str(config_file),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1
    assert "Error loading configuration" in result.stderr


def run_cli(monkeypatch, args):
    monkeypatch.setattr(sys, "argv", ["file-organizer", *args])
    return cli.main()


def test_cli_main_missing_path(monkeypatch, tmp_path, capsys):
    missing = tmp_path / "missing"
    with pytest.raises(SystemExit) as exc:
        run_cli(monkeypatch, [str(missing), "--yes"])
    assert exc.value.code == 1
    assert "does not exist" in capsys.readouterr().err


def test_cli_main_rejects_file(monkeypatch, tmp_path, capsys):
    file_path = tmp_path / "file.txt"
    file_path.write_text("hello")
    with pytest.raises(SystemExit) as exc:
        run_cli(monkeypatch, [str(file_path), "--yes"])
    assert exc.value.code == 1
    assert "not a directory" in capsys.readouterr().err


def test_cli_main_invalid_config(monkeypatch, tmp_path, capsys):
    config = tmp_path / "config.json"
    config.write_text("not json")
    with pytest.raises(SystemExit) as exc:
        run_cli(monkeypatch, [str(tmp_path), "--yes", "--config", str(config)])
    assert exc.value.code == 1
    assert "Error loading configuration" in capsys.readouterr().err


def test_cli_main_cancelled(monkeypatch, tmp_path, capsys):
    (tmp_path / "test.txt").write_text("hello")
    monkeypatch.setattr("builtins.input", lambda _: "n")
    with pytest.raises(SystemExit) as exc:
        run_cli(monkeypatch, [str(tmp_path)])
    assert exc.value.code == 0
    assert "Operation cancelled." in capsys.readouterr().out
    assert (tmp_path / "test.txt").exists()


def test_cli_main_dry_run_summary(monkeypatch, tmp_path, capsys):
    (tmp_path / "test.txt").write_text("hello")
    run_cli(monkeypatch, [str(tmp_path), "--dry-run"])
    output = capsys.readouterr().out
    assert "Dry Run Summary" in output
    assert "Files found:" in output
    assert "Files to move:        1" in output
    assert (tmp_path / "test.txt").exists()


def test_cli_main_normal_run_summary(monkeypatch, tmp_path, capsys):
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

    run_cli(monkeypatch, [str(tmp_path), "--yes", "--recursive", "--config", str(config)])
    assert (tmp_path / "Data" / "data.csv").exists()
    assert "Files moved:" in capsys.readouterr().out


def test_cli_main_reports_errors(monkeypatch, tmp_path, capsys):
    class FakeSummary:
        found = 1
        moved = 0
        duplicates_skipped = 1
        collisions_handled = 1
        errors = 1

    class FakeOrganizer:
        def __init__(self, **kwargs):
            pass

        def run(self):
            return FakeSummary()

    monkeypatch.setattr(cli, "FileOrganizer", FakeOrganizer)
    with pytest.raises(SystemExit) as exc:
        run_cli(monkeypatch, [str(tmp_path), "--yes"])
    assert exc.value.code == 1
    output = capsys.readouterr().out
    assert "Duplicates skipped:" in output
    assert "Collisions handled:" in output
    assert "Errors encountered:" in output
