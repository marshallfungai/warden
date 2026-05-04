"""
Structured logging for production
"""

import json
import logging
import sys
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """JSON formatter for Structured logging"""

    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if hasattr(record, "extra"):
            log_entry.update(record.extra)

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)


def setup_logging(level: int = logging.INFO, json_format: bool = True) -> None:
    """Configure root logger once for CLI/runtime."""
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    if json_format:
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
        )

    root_logger.handlers.clear() # clear any existing handlers to avoid duplicate logs
    root_logger.addHandler(handler)
