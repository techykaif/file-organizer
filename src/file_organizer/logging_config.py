from __future__ import annotations

import logging
import sys

LOGGER_NAME = "file_organizer"


def configure_logging(level: int = logging.INFO) -> logging.Logger:
    """Configure the application logger for CLI-friendly output."""
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(level)
    logger.propagate = False

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
        logger.addHandler(handler)

    return logger


def get_logger() -> logging.Logger:
    """Return the application logger without changing its configuration."""
    return logging.getLogger(LOGGER_NAME)
