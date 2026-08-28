from __future__ import annotations

import json
import shutil
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
            raise ValueError("history must be a list")
        return [
            [MoveRecord(str(item["source"]), str(item["destination"])) for item in operation]
            for operation in payload
        ]
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        raise ValueError(f"Invalid organizer history: {exc}") from exc


def _save_history(target_dir: Path, history: list[list[MoveRecord]]) -> None:
    path = _history_path(target_dir)
    if history:
        path.write_text(
            json.dumps([[asdict(record) for record in operation] for operation in history], indent=2),
            encoding="utf-8",
        )
    elif path.exists():
        path.unlink()


def record_operation(target_dir: Path, moves: list[MoveRecord]) -> None:
    """Record successfully completed moves for a future undo operation."""
    if not moves:
        return
    history = _load_history(target_dir)
    history.append(moves)
    _save_history(target_dir, history)


def undo_last_operation(target_dir: Path) -> tuple[int, int]:
    """Undo the most recent successful organization operation.

    Returns (restored_count, error_count). Moves are reversed in reverse order.
    Existing source paths are never overwritten.
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
        source = Path(record.source)
        destination = Path(record.destination)
        try:
            if not destination.exists():
                raise FileNotFoundError(f"Moved file not found: {destination}")
            if source.exists():
                raise FileExistsError(f"Original path already exists: {source}")
            source.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(destination), str(source))
            restored += 1
            logger.info("Restored: %s -> %s", destination.name, source)
        except (OSError, shutil.Error) as exc:
            errors += 1
            remaining.append(record)
            logger.error("Could not restore %s: %s", destination, exc)

    history[-1] = list(reversed(remaining))
    if not history[-1]:
        history.pop()
    _save_history(target_dir, history)
    return restored, errors
