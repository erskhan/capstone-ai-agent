"""Structured logging configuration."""

import logging
import sys
import json
from datetime import datetime
from typing import Any

from shared.config import get_settings


class JsonFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        if hasattr(record, "correlation_id"):
            log_data["correlation_id"] = record.correlation_id

        return json.dumps(log_data)


class ConsoleFormatter(logging.Formatter):
    """Simple console formatter for better readability."""

    COLORS = {
        "DEBUG": "\033[36m",    # Cyan
        "INFO": "\033[32m",     # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",    # Red
        "CRITICAL": "\033[35m", # Magenta
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        """Format log record for console output."""
        color = self.COLORS.get(record.levelname, self.RESET)
        timestamp = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")

        msg = f"{color}[{timestamp}] [{record.levelname:8}]{self.RESET} {record.name}: {record.getMessage()}"

        # Add correlation_id if present in record
        correlation_id = None
        if hasattr(record, "correlation_id"):
            correlation_id = record.correlation_id
        # Check if it's in the extra dict (passed via extra parameter)
        for key in record.__dict__:
            if key == "correlation_id":
                correlation_id = record.__dict__[key]
                break

        if correlation_id:
            msg = f"{msg} | correlation_id={correlation_id}"

        if record.exc_info:
            msg += f"\n{self.formatException(record.exc_info)}"

        return msg


def setup_logging() -> logging.Logger:
    """Configure structured logging."""
    settings = get_settings()

    logger = logging.getLogger("loan_approval")
    logger.setLevel(getattr(logging, settings.log_level))

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Console handler with colored output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(ConsoleFormatter())
    logger.addHandler(console_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """Get logger instance."""
    return logging.getLogger(f"loan_approval.{name}")
