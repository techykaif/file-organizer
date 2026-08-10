import importlib.metadata
import subprocess
import sys


def test_cli_help():
    result = subprocess.run(
        [sys.executable, "-m", "file_organizer.cli", "--help"],
        capture_output=True,
        text=True,
        check=False
    )
    assert result.returncode == 0
    assert "usage: file-organizer" in result.stdout

def test_cli_version():
    result = subprocess.run(
        [sys.executable, "-m", "file_organizer.cli", "--version"],
        capture_output=True,
        text=True,
        check=False
    )
    assert result.returncode == 0

    try:
        expected_version = importlib.metadata.version("kaif-file-organizer")
    except importlib.metadata.PackageNotFoundError:
        expected_version = "unknown"

    assert result.stdout.strip() == f"file-organizer {expected_version}"

def test_cli_invalid_path():
    result = subprocess.run(
        [sys.executable, "-m", "file_organizer.cli", "/path/that/does/not/exist/12345", "--yes"],
        capture_output=True,
        text=True,
        check=False
    )
    assert result.returncode == 1
    assert "does not exist" in result.stderr
