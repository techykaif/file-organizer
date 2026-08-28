from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from file_organizer.undo import MoveRecord


@dataclass(frozen=True)
class PlannedMove:
    source: Path
    destination: Path


class TransactionError(RuntimeError):
    """Raised when an organization transaction cannot be completed safely."""


def validate_plan(plan: list[PlannedMove]) -> None:
    """Validate a move plan before any filesystem mutation occurs."""
    sources = {move.source.resolve() for move in plan}
    destinations = [move.destination.resolve() for move in plan]
    if len(destinations) != len(set(destinations)):
        raise TransactionError("Move plan contains duplicate destinations")
    if sources & set(destinations):
        raise TransactionError("Move plan contains overlapping source and destination paths")


def execute_transaction(
    plan: list[PlannedMove],
    move: Callable[[Path, Path], None],
) -> list[MoveRecord]:
    """Execute moves atomically from the caller's perspective.

    If a later move fails, every move already completed is reversed. A
    TransactionError is raised after successful rollback; if rollback itself
    fails, the original error and rollback failures are retained in the message.
    """
    validate_plan(plan)
    completed: list[PlannedMove] = []

    try:
        for item in plan:
            item.destination.parent.mkdir(parents=True, exist_ok=True)
            move(item.source, item.destination)
            completed.append(item)
    except OSError as exc:
        rollback_errors: list[str] = []
        for item in reversed(completed):
            try:
                move(item.destination, item.source)
            except OSError as rollback_exc:
                rollback_errors.append(f"{item.destination}: {rollback_exc}")
        detail = f"Organization transaction failed: {exc}"
        if rollback_errors:
            detail += "; rollback failures: " + ", ".join(rollback_errors)
        raise TransactionError(detail) from exc

    return [MoveRecord(str(item.source), str(item.destination)) for item in completed]
