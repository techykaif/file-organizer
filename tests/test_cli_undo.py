import subprocess
import sys


def run_cli(*args):
    return subprocess.run(
        [sys.executable, "-m", "file_organizer.cli", *args],
        capture_output=True,
        text=True,
        check=False,
    )


def test_cli_undo_restores_last_operation(tmp_path):
    source = tmp_path / "report.txt"
    source.write_text("report")

    organize = run_cli(str(tmp_path), "--yes")
    assert organize.returncode == 0
    assert not source.exists()

    undo = run_cli(str(tmp_path), "--undo")
    assert undo.returncode == 0
    assert source.read_text() == "report"
    assert "Files restored: 1" in undo.stderr


def test_cli_undo_without_history_is_successful_noop(tmp_path):
    result = run_cli(str(tmp_path), "--undo")

    assert result.returncode == 0
    assert "Files restored: 0" in result.stderr


def test_cli_undo_rejects_conflicting_options(tmp_path):
    result = run_cli(str(tmp_path), "--undo", "--dry-run")

    assert result.returncode == 2
    assert "cannot be combined" in result.stderr
