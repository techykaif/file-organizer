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

def test_cli_dry_run(tmp_path):
    (tmp_path / "test.txt").write_text("hello")
    result = subprocess.run(
        [sys.executable, "-m", "file_organizer.cli", str(tmp_path), "--dry-run"],
        capture_output=True,
        text=True,
        check=False
    )
    assert result.returncode == 0
    assert "Would move 1 files" in result.stdout
    assert (tmp_path / "test.txt").exists()
    assert not (tmp_path / "Documents").exists()

def test_cli_normal_run(tmp_path):
    (tmp_path / "test.txt").write_text("hello")
    result = subprocess.run(
        [sys.executable, "-m", "file_organizer.cli", str(tmp_path), "--yes"],
        capture_output=True,
        text=True,
        check=False
    )
    assert result.returncode == 0
    assert "Moved 1 files" in result.stdout
    assert not (tmp_path / "test.txt").exists()
    assert (tmp_path / "Documents" / "test.txt").exists()

def test_cli_recursive(tmp_path):
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "test.jpg").write_text("image")
    result = subprocess.run(
        [sys.executable, "-m", "file_organizer.cli", str(tmp_path), "--yes", "--recursive"],
        capture_output=True,
        text=True,
        check=False
    )
    assert result.returncode == 0
    assert "Moved 1 files" in result.stdout
    assert (tmp_path / "Images" / "test.jpg").exists()
    assert not (sub / "test.jpg").exists()

def test_cli_custom_config(tmp_path):
    (tmp_path / "data.csv").write_text("1,2,3")
    config_file = tmp_path / "config.json"
    config_file.write_text('{"Data": [".csv"]}')

    result = subprocess.run(
        [sys.executable, "-m", "file_organizer.cli", str(tmp_path), "--yes", "--config", str(config_file)],
        capture_output=True,
        text=True,
        check=False
    )
    assert result.returncode == 0
    assert "Moved 2 files" in result.stdout
    assert (tmp_path / "Data" / "data.csv").exists()

def test_cli_invalid_config(tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text('invalid json')

    result = subprocess.run(
        [sys.executable, "-m", "file_organizer.cli", str(tmp_path), "--yes", "--config", str(config_file)],
        capture_output=True,
        text=True,
        check=False
    )
    assert result.returncode == 1
    assert "Error loading configuration" in result.stderr
