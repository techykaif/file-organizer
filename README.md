# kaif-file-organizer

[![CI](https://github.com/techykaif/file-organizer/actions/workflows/tests.yml/badge.svg)](https://github.com/techykaif/file-organizer/actions/workflows/tests.yml)

[![PyPI version](https://badge.fury.io/py/kaif-file-organizer.svg)](https://pypi.org/project/kaif-file-organizer/)

[![Python Versions](https://img.shields.io/pypi/pyversions/kaif-file-organizer.svg)](https://pypi.org/project/kaif-file-organizer/)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A safe, general-purpose local file organizer and file-management CLI that categorizes your files securely and predictably.

## Why this project exists

Managing a cluttered `Downloads` or `Documents` folder manually is tedious, but using automated scripts is often dangerous. Most quick-and-dirty file organizers blindly move files, leading to accidental overwrites, silent deletions, or broken symlinks.

`kaif-file-organizer` was built to provide a **production-grade, safety-first** approach to file organization. It guarantees that your files will never be automatically deleted or silently overwritten. It is designed to be a reliable utility for your daily workflow, offering dry-runs, collision detection, undo support, and extensive configurability.

## Features

- **Safe by Default**: Never deletes files automatically. Never silently overwrites files.
- **Dry-run Mode**: See what would happen before actually moving anything.
- **Duplicate Handling**: Safely handles file collisions (`file (1).ext`) and skips exact identical duplicates using MD5 hashing.
- **Configurable**: Use sensible defaults or provide your own JSON configuration for custom categories.
- **Recursive Mode**: Explicitly opt-in to process subdirectories.
- **Hidden/System Files**: Safely ignores hidden files (starting with `.`) and symlinks by default.
- **Undo**: Records successful moves and can restore the most recent organization operation without overwriting existing files.
- **Structured Logging**: Operational messages and errors use Python's logging system, with `--verbose` enabling debug output.

## Prerequisites

- Python 3.12 or higher

## Installation

You can install this tool using `pipx` (recommended) or `pip`:

```bash
# Recommended: Install isolated via pipx
pipx install kaif-file-organizer

# Alternatively, install via pip
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

## Configuration

By default, files are organized into standard categories (Documents, Images, Videos, Audio, Archives, Code, etc.).
You can override these by creating a custom JSON configuration file:

```json
{
  "Photos": [".jpg", ".png", ".heic"],
  "Work": [".pdf", ".docx", ".xlsx"],
  "Music": [".mp3", ".wav"]
}
```

And passing it via `--config`:

```bash
file-organizer ~/Downloads --config config.json
```

## Safety

File manipulation is potentially destructive, which is why `file-organizer` implements strong safety defaults:

- **Dry-run (`--dry-run`)**: Shows planned changes.
- **No silent overwrites**: Filename collisions in the destination are handled gracefully (`file (1).txt`).
- **No automatic deletion**: The tool will not delete any files or directories.
- **No hidden/system file moves**: Hidden files and symbolic links are ignored by default.
- **Undo safety**: Undo never overwrites an existing original path and preserves failed undo records for retry.

## Development

Clone the repository and install it in development mode. This project uses `uv` and the committed `uv.lock` for reproducible development environments:

```bash
git clone https://github.com/techykaif/file-organizer.git
cd file-organizer
uv sync --locked --extra dev
```

### Running Tests

Execute the full test suite:

```bash
uv run --locked pytest --cov=file_organizer --cov-fail-under=85 tests/
```

### Running Ruff

Run linting and formatting checks:

```bash
uv run --locked ruff check .
uv run --locked ruff format --check .
```

### Running Type Checks

Run the same pinned Pyright version used by CI:

```bash
uvx --from pyright==1.1.411 pyright
```

### Building the Package

Build the source distribution and wheel:

```bash
uv build
```

## Project Structure

```text
src/
└── file_organizer/
    ├── __init__.py      # Package metadata
    ├── cli.py           # CLI entry point and argument parsing
    ├── config.py        # Default categories and configuration loading
    ├── logging_config.py # Centralized structured logging configuration
    ├── organizer.py     # Core file moving and safety logic
    └── undo.py           # Operation history and safe rollback

tests/
├── test_cli.py          # CLI integration tests
├── test_cli_undo.py     # Undo CLI integration tests
├── test_logging_config.py # Logging configuration tests
├── test_organizer.py    # Unit tests for core logic
└── test_undo.py         # Undo and recovery tests
```

## Release & Development Workflow

This project uses standard GitHub Actions for CI and CD.

- **Tests**: Automatically run on every push and pull request to `main`.
- **Type checking**: Pyright runs against the `src/` package in CI.
- **Reproducibility**: CI installs development dependencies with `uv sync --locked` using the committed `uv.lock`.
- **Security**: Dependency auditing runs with `pip-audit`, and CodeQL provides separate static security scanning.
- **Releases**: Managed via GitHub Releases. Publishing a new release triggers the PyPI Trusted Publishing workflow (`release.yml`), which builds and uploads the package to PyPI securely via OIDC.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to set up your environment, run tests, and submit pull requests.

## Links

- **GitHub Repository**: [https://github.com/techykaif/file-organizer](https://github.com/techykaif/file-organizer)
- **PyPI Project**: [https://pypi.org/project/kaif-file-organizer/](https://pypi.org/project/kaif-file-organizer/)
- **Issue Tracker**: [https://github.com/techykaif/file-organizer/issues](https://github.com/techykaif/file-organizer/issues)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
