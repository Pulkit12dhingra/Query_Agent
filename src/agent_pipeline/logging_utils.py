# file+console logger, log_and_print()

"""Logging utilities for the agent pipeline."""

import logging
import os
import sys


def setup_logger(log_file_path: str = None) -> logging.Logger:
    """Setup logger with both file and console handlers."""
    if log_file_path is None:
        # Create logs directory if it doesn't exist
        log_dir = os.path.join(os.getcwd(), "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file_path = os.path.join(log_dir, "query_automation_logs.txt")

    # Create a custom logger
    logger = logging.getLogger("query_automation")
    logger.setLevel(logging.INFO)

    # Remove any existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create file handler that appends to the log file
    file_handler = logging.FileHandler(log_file_path, mode="a")
    file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(file_formatter)

    # Create console handler for stdout
    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = logging.Formatter("%(message)s")
    console_handler.setFormatter(console_formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# Global logger instance
_logger = None


def get_logger() -> logging.Logger:
    """Get the global logger instance."""
    global _logger
    if _logger is None:
        _logger = setup_logger()
    return _logger


def log_and_print(message: str, level: str = "info"):
    """Log message to both file and console"""
    logger = get_logger()
    if level.lower() == "info":
        logger.info(message)
    elif level.lower() == "error":
        logger.error(message)
    elif level.lower() == "warning":
        logger.warning(message)
