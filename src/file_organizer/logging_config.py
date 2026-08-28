from __future__ import annotations

import logging
import sys

LOGGER_NAME = "file_organizer"


class _DynamicStderrHandler(logging.StreamHandler):
    """Write to the current stderr stream so CLI and test capture both work."""

    def emit(self, record: logging.LogRecord) -> None:
        self.stream = sys.stderr
        super().emit(record)


def configure_logging(level: int = logging.INFO) -> logging.Logger:
    """Configure the application logger for CLI-friendly output."""
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(level)
    logger.propagate = False

    if not logger.handlers:
        handler = _DynamicStderrHandler()
        handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
        logger.addHandler(handler)
    else:
        for handler in logger.handlers:
            if isinstance(handler, _DynamicStderrHandler):
                handler.stream = sys.stderr

    return logger


def get_logger() -> logging.Logger:
    """Return the application logger without changing its configuration."""
    return logging.getLogger(LOGGER_NAME)
