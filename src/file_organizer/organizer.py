from __future__ import annotations

import hashlib
import os
import shutil
from dataclasses import dataclass
from pathlib import Path

from file_organizer.config import DEFAULT_CATEGORIES, get_category_for_extension
from file_organizer.logging_config import get_logger
from file_organizer.undo import MoveRecord, record_operation

logger = get_logger()


@dataclass
class OrganizerSummary:
    found: int = 0
    moved: int = 0
    duplicates_skipped: int = 0
    collisions_handled: int = 0
    errors: int = 0


class FileOrganizer:
    def __init__(
        self,
        target_dir: Path,
        categories: dict[str, list[str]] | None = None,
        dry_run: bool = False,
        recursive: bool = False,
    ):
        self.target_dir = target_dir.resolve()
        self.categories = categories if categories is not None else DEFAULT_CATEGORIES
        self.dry_run = dry_run
        self.recursive = recursive
        self.processed_hashes: set[str] = set()

    def _calculate_hash(self, file_path: Path) -> str | None:
        """Calculate MD5 hash of a file safely."""
        try:
            hash_algo = hashlib.md5()
            with open(file_path, "rb") as f:
                while chunk := f.read(8192):
                    hash_algo.update(chunk)
            return hash_algo.hexdigest()
        except (PermissionError, OSError) as e:
            logger.warning("Could not read %s for hashing: %s", file_path, e)
            return None

    def _get_safe_destination(
        self, source_path: Path, dest_dir: Path
    ) -> tuple[Path, bool]:
        """Find a safe filename using file (1).ext format if a collision occurs.

        Returns (dest_path, collision_occurred).
        """
        base_name = source_path.stem
        ext = source_path.suffix
        dest_path = dest_dir / source_path.name
        counter = 1
        collision = False
        while dest_path.exists():
            collision = True
            dest_path = dest_dir / f"{base_name} ({counter}){ext}"
            counter += 1
        return dest_path, collision

    def _is_safe_to_process(self, path: Path) -> bool:
        """Check if a file should be skipped (hidden or system file)."""
        if path.name.startswith("."):
            return False
        return not path.is_symlink()

    def run(self) -> OrganizerSummary:
        """Run the file organization. Returns an OrganizerSummary."""
        summary = OrganizerSummary()
        completed_moves: list[MoveRecord] = []

        if not self.target_dir.exists():
            logger.error("Target directory '%s' does not exist.", self.target_dir)
            summary.errors += 1
            return summary

        if not self.target_dir.is_dir():
            logger.error("Target '%s' is not a directory.", self.target_dir)
            summary.errors += 1
            return summary

        files_to_process: list[Path] = []
        try:
            if self.recursive:
                for root, dirs, files in os.walk(self.target_dir):
                    root_path = Path(root)
                    dirs[:] = [
                        d
                        for d in dirs
                        if not d.startswith(".")
                        and d not in self.categories
                        and d != "Other"
                    ]
                    for file in files:
                        file_path = root_path / file
                        if self._is_safe_to_process(file_path):
                            files_to_process.append(file_path)
            else:
                for item in self.target_dir.iterdir():
                    if item.is_file() and self._is_safe_to_process(item):
                        files_to_process.append(item)
        except PermissionError as e:
            logger.error("Permission denied accessing directory contents: %s", e)
            summary.errors += 1
            return summary

        summary.found = len(files_to_process)
        logger.info("Found %d files to process.", summary.found)

        for file_path in files_to_process:
            try:
                file_hash = self._calculate_hash(file_path)
                if file_hash:
                    if file_hash in self.processed_hashes:
                        logger.info("Skipping duplicate file: %s", file_path.name)
                        summary.duplicates_skipped += 1
                        continue
                    self.processed_hashes.add(file_hash)

                category = get_category_for_extension(file_path.suffix, self.categories)
                dest_dir = self.target_dir / category
                dest_path, collision = self._get_safe_destination(file_path, dest_dir)
                if collision:
                    summary.collisions_handled += 1

                if self.dry_run:
                    display_path = (
                        file_path.relative_to(self.target_dir)
                        if self.recursive
                        else file_path.name
                    )
                    logger.info(
                        "[DRY-RUN] Would move: %s -> %s/%s",
                        display_path,
                        category,
                        dest_path.name,
                    )
                else:
                    dest_dir.mkdir(exist_ok=True, parents=True)
                    shutil.move(str(file_path), str(dest_path))
                    completed_moves.append(
                        MoveRecord(str(file_path), str(dest_path))
                    )
                    logger.info(
                        "Moved: %s -> %s/%s", file_path.name, category, dest_path.name
                    )
                summary.moved += 1
            except PermissionError:
                logger.error("Permission denied moving %s", file_path.name)
                summary.errors += 1
            except OSError as e:
                logger.error("Error processing %s: %s", file_path.name, e)
                summary.errors += 1

        if not self.dry_run and completed_moves:
            try:
                record_operation(self.target_dir, completed_moves)
            except (OSError, ValueError) as exc:
                logger.error("Could not save undo history: %s", exc)
                summary.errors += 1

        return summary
