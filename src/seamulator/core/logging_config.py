"""Logging configuration for the maritime traffic simulator."""

import logging


def setup_logging() -> logging.Logger:
    """Set up and configure logging for the application.

    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger("seamulator")
    logger.setLevel(logging.DEBUG)

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(console_handler)

    return logger


# Global logger instance
logger = setup_logging()
