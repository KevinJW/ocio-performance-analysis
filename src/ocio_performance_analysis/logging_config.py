"""
Centralized logging configuration for OCIO Performance Analysis.
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    console: bool = True,
    format_str: Optional[str] = None
) -> logging.Logger:
    """
    Configure logging for the OCIO performance analysis toolkit.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for log output
        console: Whether to enable console logging
        format_str: Custom format string for log messages

    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger("ocio_performance_analysis")
    logger.setLevel(getattr(logging, level.upper()))

    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()

    # Default format with emojis for better UX
    if format_str is None:
        format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    formatter = logging.Formatter(format_str)

    # Console handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level.upper()))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # File handler
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)  # Always log everything to file
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str = "ocio_performance_analysis") -> logging.Logger:
    """
    Get a logger instance for the specified module.

    Args:
        name: Logger name, typically __name__ from calling module

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


# Configure default logger on import
default_logger = setup_logging()
