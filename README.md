# File Organizer

A safe, general-purpose local file organizer and file-management CLI that categorizes your files securely and predictably.

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
pipx install git+https://github.com/techykaif/file_handling.git

# Alternatively, install via pip
pip install git+https://github.com/techykaif/file_handling.git
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
git clone https://github.com/techykaif/file_handling.git
cd file_handling
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Run tests and linting:
```bash
pytest
ruff check .
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
