import pytest

from file_organizer.undo import (
    HISTORY_FILENAME,
    MoveRecord,
    record_operation,
    undo_last_operation,
)


def test_record_and_undo_last_operation(tmp_path):
    source = tmp_path / "report.txt"
    source.write_text("report")
    destination = tmp_path / "Documents" / "report.txt"
    destination.parent.mkdir()
    source.rename(destination)

    record_operation(tmp_path, [MoveRecord(str(source), str(destination))])

    restored, errors = undo_last_operation(tmp_path)

    assert (restored, errors) == (1, 0)
    assert source.read_text() == "report"
    assert not destination.exists()
    assert not (tmp_path / HISTORY_FILENAME).exists()


def test_undo_does_not_overwrite_existing_source(tmp_path):
    source = tmp_path / "report.txt"
    source.write_text("new content")
    destination = tmp_path / "Documents" / "report.txt"
    destination.parent.mkdir()
    destination.write_text("organized content")

    record_operation(tmp_path, [MoveRecord(str(source), str(destination))])

    restored, errors = undo_last_operation(tmp_path)

    assert (restored, errors) == (0, 1)
    assert source.read_text() == "new content"
    assert destination.read_text() == "organized content"
    assert (tmp_path / HISTORY_FILENAME).exists()


def test_undo_missing_history_is_noop(tmp_path):
    assert undo_last_operation(tmp_path) == (0, 0)


def test_undo_keeps_failed_records_and_restores_successful_records(tmp_path):
    source_ok = tmp_path / "ok.txt"
    source_ok.write_text("ok")
    destination_ok = tmp_path / "Documents" / "ok.txt"
    destination_ok.parent.mkdir()
    source_ok.rename(destination_ok)

    source_conflict = tmp_path / "conflict.txt"
    source_conflict.write_text("original")
    destination_conflict = tmp_path / "Documents" / "conflict.txt"
    destination_conflict.write_text("moved")

    record_operation(
        tmp_path,
        [
            MoveRecord(str(source_ok), str(destination_ok)),
            MoveRecord(str(source_conflict), str(destination_conflict)),
        ],
    )

    restored, errors = undo_last_operation(tmp_path)

    assert (restored, errors) == (1, 1)
    assert source_ok.exists()
    assert destination_conflict.exists()
    assert source_conflict.read_text() == "original"


def test_undo_rejects_invalid_history(tmp_path):
    (tmp_path / HISTORY_FILENAME).write_text("not json")

    with pytest.raises(ValueError, match="Invalid organizer history"):
        undo_last_operation(tmp_path)
