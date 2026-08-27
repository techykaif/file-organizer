from __future__ import annotations

import json
from pathlib import Path

DEFAULT_CATEGORIES = {
    "Documents": [".pdf", ".docx", ".txt", ".doc", ".odt", ".rtf"],
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp"],
    "Videos": [".mp4", ".mkv", ".avi", ".mov", ".wmv"],
    "Audio": [".mp3", ".wav", ".flac", ".m4a", ".aac"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"],
    "Executables": [".exe", ".msi", ".bat", ".sh"],
    "Python Scripts": [".py"],
    "Applications": [".app", ".dmg", ".pkg"],
    "Web Pages": [".html", ".xml", ".css", ".js"],
    "Spreadsheets": [".xls", ".xlsx", ".csv", ".ods"],
    "Presentations": [".ppt", ".pptx", ".odp"],
    "Code": [".cpp", ".java", ".c", ".h", ".cs", ".json", ".yaml", ".yml"],
}


def load_config(config_path: Path) -> dict[str, list[str]]:
    """
    Load categorization configuration from a JSON file.
    Falls back to DEFAULT_CATEGORIES if not provided.
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        try:
            user_categories = json.load(f)
            if not isinstance(user_categories, dict):
                raise TypeError(
                    "Configuration must be a JSON object mapping category names to lists of extensions."
                )
            return user_categories
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file: {e}")


def get_category_for_extension(ext: str, categories: dict[str, list[str]]) -> str:
    """Return the category name for a given extension, or 'Other' if not found."""
    ext = ext.lower()
    for category, extensions in categories.items():
        if ext in [e.lower() for e in extensions]:
            return category
    return "Other"
