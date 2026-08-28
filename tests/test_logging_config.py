import logging

from file_organizer.logging_config import configure_logging, get_logger


def test_configure_logging_sets_level():
    logger = configure_logging(logging.DEBUG)
    assert logger is get_logger()
    assert logger.level == logging.DEBUG
    assert logger.handlers


def test_configure_logging_reuses_handler():
    logger = configure_logging(logging.INFO)
    handler_count = len(logger.handlers)
    configure_logging(logging.DEBUG)
    assert len(logger.handlers) == handler_count
    assert logger.level == logging.DEBUG


def test_configure_logging_emits_formatted_message(capsys):
    logger = configure_logging(logging.INFO)
    logger.info("hello %s", "world")
    assert "INFO: hello world" in capsys.readouterr().err
