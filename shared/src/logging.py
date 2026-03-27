"""
Structured logging configuration
"""
import logging
import json
import sys
from logging.handlers import RotatingFileHandler
from datetime import datetime
from pythonjsonlogger import jsonlogger


class PACTAJSONFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter for PACTA logs."""

    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        log_record["timestamp"] = datetime.utcnow().isoformat()
        log_record["level"] = record.levelname
        log_record["logger"] = record.name
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)


def get_logger(name: str, log_level: str = "INFO") -> logging.Logger:
    """
    Get a configured logger instance.

    Args:
        name: Logger name (typically __name__)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Console handler with JSON formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_formatter = PACTAJSONFormatter()
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler (optional)
    try:
        file_handler = RotatingFileHandler(
            "logs/pacta.log",
            maxBytes=10_485_760,  # 10MB
            backupCount=10,
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(console_formatter)
        logger.addHandler(file_handler)
    except Exception:
        pass  # Silently fail if log directory doesn't exist

    return logger
