# kaif-file-organizer

[![CI](https://github.com/techykaif/file-organizer/actions/workflows/tests.yml/badge.svg)](https://github.com/techykaif/file-organizer/actions/workflows/tests.yml)

[![PyPI version](https://badge.fury.io/py/kaif-file-organizer.svg)](https://pypi.org/project/kaif-file-organizer/)

[![Python Versions](https://img.shields.io/pypi/pyversions/kaif-file-organizer.svg)](https://pypi.org/project/kaif-file-organizer/)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A safe, general-purpose local file organizer and file-management CLI that categorizes your files securely and predictably.

## Why this project exists

Managing a cluttered `Downloads` or `Documents` folder manually is tedious, but automated scripts can be dangerous. Quick file organizers may overwrite files, delete data, or follow links unexpectedly.

`kaif-file-organizer` takes a **safety-first** approach. It never automatically deletes files or silently overwrites destination files. It supports dry-runs, collision handling, duplicate detection, recursive organization, configurable categories, undo, structured logging, and transaction-style rollback when a move operation fails.

## Features

- **Safe by Default**: Never deletes files automatically or silently overwrites destination files.
- **Dry-run Mode**: Preview planned changes without moving files.
- **Duplicate Handling**: Skips exact identical duplicates using MD5 hashing and handles filename collisions with `file (1).ext` naming.
- **Configurable**: Use sensible defaults or provide a custom JSON category configuration.
- **Recursive Mode**: Explicitly opt in to processing subdirectories.
- **Hidden/System Files**: Ignores hidden files and symbolic links by default.
- **Undo**: Records successful moves and restores the most recent organization operation without overwriting existing original paths.
- **Transaction Safety**: Plans moves before mutation, validates destinations, and attempts to roll back completed moves if a later move fails.
- **Structured Logging**: Uses Python's logging system for operational messages and errors, with `--verbose` enabling debug output.

## Prerequisites

- Python 3.12 or higher

## Installation

Install the published package with `pipx` (recommended) or `pip`:

```bash
# Recommended: install in an isolated environment
pipx install kaif-file-organizer

# Alternatively
pip install kaif-file-organizer
```

## Usage

Organize a directory:

```bash
file-organizer ~/Downloads
```

Preview changes without moving files:

```bash
file-organizer ~/Downloads --dry-run
```

Organize a directory and its subdirectories:

```bash
file-organizer ~/Downloads --recursive
```

Use a custom configuration:

```bash
file-organizer ~/Downloads --config my_categories.json
```

Skip confirmation prompts (for automation):

```bash
file-organizer ~/Downloads --yes
```

Undo the most recent successful organization:

```bash
file-organizer ~/Downloads --undo
```

`--undo` restores recorded moves in reverse order and refuses to overwrite an existing original path. If part of an undo cannot be completed, the failed records remain available for a later retry.

Enable verbose logging:

```bash
file-organizer ~/Downloads --yes --verbose
```

## Safety and failure behavior

File manipulation is potentially destructive, so safety is a core design goal:

- **Dry-run (`--dry-run`)** shows the planned changes before mutation.
- **No silent overwrites**: destination collisions use a new filename such as `file (1).txt`.
- **No automatic deletion**: the organizer does not delete files or directories.
- **No hidden/system file moves**: hidden files and symbolic links are ignored by default.
- **Transaction-style organization**: moves are planned and validated before execution. If a later move fails, completed moves are reversed when possible. If rollback itself fails, the error reports the rollback failures instead of hiding the partial state.
- **Undo safety**: undo never overwrites an existing original path and preserves failed undo records for retry.

Transaction rollback is best-effort filesystem recovery, not a database-style atomic transaction: failures outside the process's control can still prevent a complete rollback.

## Configuration

By default, files are organized into standard categories (Documents, Images, Videos, Audio, Archives, Code, and others). You can override these categories with a JSON configuration file:

```json
{
  "Photos": [".jpg", ".png", ".heic"],
  "Work": [".pdf", ".docx", ".xlsx"],
  "Music": [".mp3", ".wav"]
}
```

Then pass it with `--config`:

```bash
file-organizer ~/Downloads --config config.json
```

## Development

This project uses `uv` and the committed `uv.lock` for reproducible development environments.

```bash
git clone https://github.com/techykaif/file-organizer.git
cd file-organizer
uv sync --locked --extra dev
```

The CI pipeline also validates this setup from a fresh clone and verifies the package build and wheel installation.

### Tests and coverage

```bash
uv run --locked pytest --cov=file_organizer --cov-fail-under=85 tests/
```

### Ruff

```bash
uv run --locked ruff check .
uv run --locked ruff format --check .
```

Apply formatting locally with:

```bash
uv run --locked ruff format .
```

### Type checks

Run the same pinned Pyright version used by CI:

```bash
uvx --from pyright==1.1.411 pyright
```

### Build

```bash
uv build
```

## Project Structure

```text
src/
└── file_organizer/
    ├── __init__.py          # Package metadata
    ├── cli.py               # CLI entry point and argument parsing
    ├── config.py            # Default categories and configuration loading
    ├── logging_config.py    # Centralized logging configuration
    ├── organizer.py         # Core file discovery, planning, and organization
    ├── transaction.py       # Move validation, execution, and rollback
    └── undo.py              # Operation history and safe undo

tests/
├── test_cli.py              # CLI integration tests
├── test_cli_undo.py         # Undo CLI integration tests
├── test_logging_config.py   # Logging configuration tests
├── test_organizer.py        # Core organizer behavior
├── test_transaction.py      # Transaction validation and rollback tests
└── test_undo.py             # Undo and recovery tests
```

## CI and release workflow

GitHub Actions runs the authoritative checks on pushes and pull requests targeting `main`:

- **Linting and formatting** with Ruff.
- **Type checking** with the pinned Pyright version.
- **Tests and coverage** with an 85% minimum coverage gate.
- **Build/install smoke testing** for the generated package and wheel.
- **Fresh-clone verification** of the documented locked development setup.
- **Dependency auditing** with `pip-audit`.
- **CodeQL** security scanning through a separate workflow.

Development dependencies are installed with `uv sync --locked` using the committed `uv.lock`, keeping CI and local development reproducible.

Releases are managed through GitHub Releases. Publishing a release triggers the PyPI Trusted Publishing workflow (`release.yml`), which builds and uploads the package securely via OIDC.

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for the complete development and pull-request workflow.

## Links

- **GitHub Repository**: https://github.com/techykaif/file-organizer
- **PyPI Project**: https://pypi.org/project/kaif-file-organizer/
- **Issue Tracker**: https://github.com/techykaif/file-organizer/issues

## License

This project is licensed under the MIT License. See `LICENSE` for details.
