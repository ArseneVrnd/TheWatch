# TheWatch/utils/logger.py
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


def setup_logger(name: str, log_file: Optional[str] = None) -> logging.Logger:
    """
    Setup a logger with console and optional file output

    Args:
        name: Name of the logger
        log_file: Optional path to log file

    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create formatters
    console_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # Create file handler if log_file specified
    if log_file:
        # Create logs directory if it doesn't exist
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)

        # Create file handler
        file_handler = logging.FileHandler(
            log_dir / f"{log_file}_{datetime.now().strftime('%Y%m%d')}.log"
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


# Create helpers for specific loggers
def get_scraper_logger() -> logging.Logger:
    """Get logger for scraper module"""
    return setup_logger('scraper', 'scraper')


def get_api_logger() -> logging.Logger:
    """Get logger for API module"""
    return setup_logger('api', 'api')


def get_monitor_logger() -> logging.Logger:
    """Get logger for monitor module"""
    return setup_logger('monitor', 'monitor')


# Export functions
__all__ = ['setup_logger', 'get_scraper_logger', 'get_api_logger', 'get_monitor_logger']