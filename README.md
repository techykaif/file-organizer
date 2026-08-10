# kaif-file-organizer

[![CI](https://github.com/techykaif/file-organizer/actions/workflows/tests.yml/badge.svg)](https://github.com/techykaif/file-organizer/actions/workflows/tests.yml)

[![PyPI version](https://badge.fury.io/py/kaif-file-organizer.svg)](https://pypi.org/project/kaif-file-organizer/)

[![Python Versions](https://img.shields.io/pypi/pyversions/kaif-file-organizer.svg)](https://pypi.org/project/kaif-file-organizer/)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A safe, general-purpose local file organizer and file-management CLI that categorizes your files securely and predictably.

## Why this project exists

Managing a cluttered `Downloads` or `Documents` folder manually is tedious, but using automated scripts is often dangerous. Most quick-and-dirty file organizers blindly move files, leading to accidental overwrites, silent deletions, or broken symlinks.

`kaif-file-organizer` was built to provide a **production-grade, safety-first** approach to file organization. It guarantees that your files will never be automatically deleted or silently overwritten. It is designed to be a reliable utility for your daily workflow, offering dry-runs, collision detection, and extensive configurability.

## Features

- **Safe by Default**: Never deletes files automatically. Never silently overwrites files.
- **Dry-run Mode**: See what would happen before actually moving anything.
- **Duplicate Handling**: Safely handles file collisions (`file (1).ext`) and skips exact identical duplicates using MD5 hashing.
- **Configurable**: Use sensible defaults or provide your own JSON configuration for custom categories.
- **Recursive Mode**: Explicitly opt-in to process subdirectories.
- **Hidden/System Files**: Safely ignores hidden files (starting with `.`) and symlinks by default.

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

## Development

Clone the repository and install it in development mode:

```bash
git clone https://github.com/techykaif/file-organizer.git
cd file-organizer
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Running Tests

Execute the test suite using pytest:

```bash
pytest tests/
```

### Running Ruff

Run linting and formatting checks:

```bash
ruff check .
```

### Building the Package

Build the source distribution and wheel:

```bash
python -m pip install build
python -m build
```

## Project Structure

```text
src/
└── file_organizer/
    ├── __init__.py      # Package metadata
    ├── cli.py           # CLI entry point and argument parsing
    ├── config.py        # Default categories and configuration loading
    └── organizer.py     # Core file moving and safety logic
tests/
├── test_cli.py          # CLI integration tests
└── test_organizer.py    # Unit tests for core logic
```

## Release & Development Workflow

This project uses standard GitHub Actions for CI and CD.

- **Tests**: Automatically run on every push and pull request to `main`.
- **Releases**: Managed via GitHub Releases. Publishing a new release triggers the PyPI Trusted Publishing workflow (`release.yml`), which builds and uploads the package to PyPI securely via OIDC.

## Links

- **GitHub Repository**: [https://github.com/techykaif/file-organizer](https://github.com/techykaif/file-organizer)
- **PyPI Project**: [https://pypi.org/project/kaif-file-organizer/](https://pypi.org/project/kaif-file-organizer/)
- **Issue Tracker**: [https://github.com/techykaif/file-organizer/issues](https://github.com/techykaif/file-organizer/issues)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
