"""
Structured logging for production
"""

import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict


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

    def setup_logging(level=logging.INFO, json_format: bool = True):
        """Seup logging with JSONformatter for production"""
        root_logger = logging.getLogger()
        root_logger
