from pathlib import Path

import pytest

from file_organizer.transaction import (
    PlannedMove,
    TransactionError,
    execute_transaction,
    validate_plan,
)


def test_validate_plan_rejects_duplicate_destinations(tmp_path):
    source_a = tmp_path / "a.txt"
    source_b = tmp_path / "b.txt"
    destination = tmp_path / "Documents" / "same.txt"

    with pytest.raises(TransactionError, match="duplicate destinations"):
        validate_plan(
            [
                PlannedMove(source_a, destination),
                PlannedMove(source_b, destination),
            ]
        )


def test_validate_plan_rejects_overlapping_paths(tmp_path):
    source = tmp_path / "a.txt"
    destination = tmp_path / "b.txt"

    with pytest.raises(TransactionError, match="overlapping"):
        validate_plan(
            [
                PlannedMove(source, destination),
                PlannedMove(destination, tmp_path / "c.txt"),
            ]
        )


def test_execute_transaction_returns_records(tmp_path):
    source_a = tmp_path / "a.txt"
    source_b = tmp_path / "b.txt"
    source_a.write_text("a")
    source_b.write_text("b")
    destination_a = tmp_path / "Documents" / "a.txt"
    destination_b = tmp_path / "Documents" / "b.txt"

    def move(source: Path, destination: Path) -> None:
        source.rename(destination)

    records = execute_transaction(
        [
            PlannedMove(source_a, destination_a),
            PlannedMove(source_b, destination_b),
        ],
        move,
    )

    assert len(records) == 2
    assert destination_a.read_text() == "a"
    assert destination_b.read_text() == "b"


def test_execute_transaction_rolls_back_completed_moves(tmp_path):
    source_a = tmp_path / "a.txt"
    source_b = tmp_path / "b.txt"
    source_a.write_text("a")
    source_b.write_text("b")
    destination_a = tmp_path / "Documents" / "a.txt"
    destination_b = tmp_path / "Documents" / "b.txt"
    calls = 0

    def move(source: Path, destination: Path) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("disk full")
        source.rename(destination)

    with pytest.raises(TransactionError, match="Organization transaction failed"):
        execute_transaction(
            [
                PlannedMove(source_a, destination_a),
                PlannedMove(source_b, destination_b),
            ],
            move,
        )

    assert source_a.read_text() == "a"
    assert source_b.read_text() == "b"
    assert not destination_a.exists()


def test_execute_transaction_reports_rollback_failure(tmp_path):
    source_a = tmp_path / "a.txt"
    source_b = tmp_path / "b.txt"
    source_a.write_text("a")
    source_b.write_text("b")
    destination_a = tmp_path / "Documents" / "a.txt"
    destination_b = tmp_path / "Documents" / "b.txt"
    calls = 0

    def move(source: Path, destination: Path) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("disk full")
        if calls == 3:
            raise OSError("rollback blocked")
        source.rename(destination)

    with pytest.raises(TransactionError, match="rollback failures"):
        execute_transaction(
            [
                PlannedMove(source_a, destination_a),
                PlannedMove(source_b, destination_b),
            ],
            move,
        )

    assert destination_a.exists()
