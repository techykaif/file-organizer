import argparse
import logging
import sys
from pathlib import Path

from file_organizer import __version__
from file_organizer.config import load_config
from file_organizer.logging_config import configure_logging
from file_organizer.organizer import FileOrganizer
from file_organizer.undo import undo_last_operation


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="file-organizer",
        description="A safe, general-purpose local file organizer and file-management CLI.",
    )
    parser.add_argument("path", type=str, help="The directory to organize.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would happen without making any changes.",
    )
    parser.add_argument(
        "--recursive", action="store_true", help="Recursively process subdirectories."
    )
    parser.add_argument(
        "--config",
        type=str,
        help="Path to a custom JSON configuration file mapping categories to extensions.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip any confirmation prompts (non-interactive mode).",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose informational logging.",
    )
    parser.add_argument(
        "--undo",
        action="store_true",
        help="Undo the most recent successful organization operation.",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )

    args = parser.parse_args()
    logger = configure_logging(logging.DEBUG if args.verbose else logging.INFO)
    target_path = Path(args.path)

    if not target_path.exists():
        logger.error("Path '%s' does not exist.", target_path)
        sys.exit(1)
    if not target_path.is_dir():
        logger.error("Path '%s' is not a directory.", target_path)
        sys.exit(1)

    if args.undo:
        if any((args.dry_run, args.recursive, args.config, args.yes)):
            logger.error("--undo cannot be combined with organization options.")
            sys.exit(2)
        restored, errors = undo_last_operation(target_path.resolve())
        logger.info("--- Undo Summary ---")
        logger.info("Files restored: %d", restored)
        if errors:
            logger.error("Errors encountered: %d", errors)
            sys.exit(1)
        sys.exit(0)

    categories = None
    if args.config:
        try:
            categories = load_config(Path(args.config))
        except (ValueError, OSError) as e:
            logger.error("Error loading configuration: %s", e)
            sys.exit(1)

    if not args.yes and not args.dry_run:
        confirm = (
            input(
                f"Are you sure you want to organize '{target_path.resolve()}'? [y/N]: "
            )
            .strip()
            .lower()
        )
        if confirm not in ["y", "yes"]:
            logger.info("Operation cancelled.")
            sys.exit(0)

    summary = FileOrganizer(
        target_dir=target_path,
        categories=categories,
        dry_run=args.dry_run,
        recursive=args.recursive,
    ).run()

    if args.dry_run:
        logger.info("--- Dry Run Summary ---")
        logger.info("Files found:          %d", summary.found)
        logger.info("Files to move:        %d", summary.moved)
        if summary.duplicates_skipped > 0:
            logger.info("Duplicates to skip:   %d", summary.duplicates_skipped)
        if summary.collisions_handled > 0:
            logger.info("Collisions to handle: %d", summary.collisions_handled)
        if summary.errors > 0:
            logger.error("Errors encountered:   %d", summary.errors)
    else:
        logger.info("--- Organization Summary ---")
        logger.info("Files found:          %d", summary.found)
        logger.info("Files moved:          %d", summary.moved)
        if summary.duplicates_skipped > 0:
            logger.info("Duplicates skipped:   %d", summary.duplicates_skipped)
        if summary.collisions_handled > 0:
            logger.info("Collisions handled:   %d", summary.collisions_handled)
        if summary.errors > 0:
            logger.error("Errors encountered:   %d", summary.errors)

    if summary.errors > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
