from __future__ import annotations

import json
import os
import shutil
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path

from file_organizer.logging_config import get_logger

logger = get_logger()
HISTORY_FILENAME = ".file-organizer-history.json"


@dataclass
class MoveRecord:
    source: str
    destination: str


def _history_path(target_dir: Path) -> Path:
    return target_dir / HISTORY_FILENAME


def _load_history(target_dir: Path) -> list[list[MoveRecord]]:
    path = _history_path(target_dir)
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, list):
            raise TypeError("history must be a list")

        history: list[list[MoveRecord]] = []
        for operation in payload:
            if not isinstance(operation, list):
                raise TypeError("each history operation must be a list")
            records: list[MoveRecord] = []
            for item in operation:
                if not isinstance(item, dict):
                    raise TypeError("each history record must be an object")
                source = item.get("source")
                destination = item.get("destination")
                if not isinstance(source, str) or not source:
                    raise TypeError("history source must be a non-empty string")
                if not isinstance(destination, str) or not destination:
                    raise TypeError("history destination must be a non-empty string")
                records.append(MoveRecord(source, destination))
            history.append(records)
        return history
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Invalid organizer history: {exc}") from exc


def _save_history(target_dir: Path, history: list[list[MoveRecord]]) -> None:
    path = _history_path(target_dir)
    if not history:
        if path.exists():
            path.unlink()
        return

    payload = json.dumps(
        [[asdict(record) for record in operation] for operation in history],
        indent=2,
    )
    temp_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=target_dir,
            prefix=".file-organizer-history-",
            delete=False,
        ) as temp_file:
            temp_file.write(payload)
            temp_file.flush()
            os.fsync(temp_file.fileno())
            temp_path = temp_file.name
        os.replace(temp_path, path)
        temp_path = None
    finally:
        if temp_path is not None:
            try:
                os.unlink(temp_path)
            except FileNotFoundError:
                pass


def record_operation(target_dir: Path, moves: list[MoveRecord]) -> None:
    """Record successfully completed moves for a future undo operation."""
    if not moves:
        return
    history = _load_history(target_dir)
    history.append(moves)
    _save_history(target_dir, history)


def _safe_path(target_dir: Path, value: str) -> Path:
    """Resolve a history path and reject paths outside the organizer root."""
    root = target_dir.resolve()
    candidate = Path(value).resolve(strict=False)
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"History path is outside target directory: {value}") from exc
    return candidate


def undo_last_operation(target_dir: Path) -> tuple[int, int]:
    """Undo the most recent successful organization operation.

    Returns (restored_count, error_count). Moves are reversed in reverse order.
    Existing source paths are never overwritten, and history cannot move files
    outside the organizer's target directory.
    """
    history = _load_history(target_dir)
    if not history:
        logger.info("No organization operation is available to undo.")
        return 0, 0

    operation = history[-1]
    restored = 0
    errors = 0
    remaining: list[MoveRecord] = []

    for record in reversed(operation):
        try:
            source = _safe_path(target_dir, record.source)
            destination = _safe_path(target_dir, record.destination)
            if not destination.exists():
                raise FileNotFoundError(f"Moved file not found: {destination}")
            if source.exists():
                raise FileExistsError(f"Original path already exists: {source}")
            source.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(destination), str(source))
            restored += 1
            logger.info("Restored: %s -> %s", destination.name, source)
        except (OSError, shutil.Error, ValueError) as exc:
            errors += 1
            remaining.append(record)
            logger.error("Could not restore %s: %s", record.destination, exc)

    history[-1] = list(reversed(remaining))
    if not history[-1]:
        history.pop()
    _save_history(target_dir, history)
    return restored, errors
