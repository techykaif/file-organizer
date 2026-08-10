import argparse
import sys
from pathlib import Path

from file_organizer import __version__
from file_organizer.config import load_config
from file_organizer.organizer import FileOrganizer


def main():
    parser = argparse.ArgumentParser(
        prog="file-organizer",
        description="A safe, general-purpose local file organizer and file-management CLI.",
    )

    parser.add_argument("path", type=str, help="The directory to organize.")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen without making any changes.")
    parser.add_argument("--recursive", action="store_true", help="Recursively process subdirectories.")
    parser.add_argument("--config", type=str, help="Path to a custom JSON configuration file mapping categories to extensions.")
    parser.add_argument("--yes", action="store_true", help="Skip any confirmation prompts (non-interactive mode).")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    args = parser.parse_args()

    target_path = Path(args.path)

    if not target_path.exists():
        print(f"Error: Path '{target_path}' does not exist.", file=sys.stderr)
        sys.exit(1)

    if not target_path.is_dir():
        print(f"Error: Path '{target_path}' is not a directory.", file=sys.stderr)
        sys.exit(1)

    categories = None
    if args.config:
        config_path = Path(args.config)
        try:
            categories = load_config(config_path)
        except (ValueError, OSError) as e:
            print(f"Error loading configuration: {e}", file=sys.stderr)
            sys.exit(1)

    if not args.yes and not args.dry_run:
        # Prompt for confirmation if it's a real run
        confirm = input(f"Are you sure you want to organize '{target_path.resolve()}'? [y/N]: ").strip().lower()
        if confirm not in ['y', 'yes']:
            print("Operation cancelled.")
            sys.exit(0)

    organizer = FileOrganizer(
        target_dir=target_path,
        categories=categories,
        dry_run=args.dry_run,
        recursive=args.recursive
    )

    moved, errors = organizer.run()

    if args.dry_run:
        print(f"\nDry run complete. Would move {moved} files. Errors encountered: {errors}.")
    else:
        print(f"\nOrganization complete. Moved {moved} files. Errors encountered: {errors}.")

    if errors > 0:
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()
