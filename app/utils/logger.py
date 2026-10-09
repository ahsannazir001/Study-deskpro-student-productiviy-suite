"""Application logging utilities.

Provides a configured logger that writes to a rotating file in the user data
directory and to the console. Sensitive data is never logged.
"""

import logging
import os
from logging.handlers import RotatingFileHandler

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_initialized = False
_log_dir = None


def init_logging(log_dir):
    """Initialize the root logger. Safe to call once at startup."""
    global _initialized, _log_dir
    if _initialized:
        return get_logger()
    _log_dir = str(log_dir)
    try:
        os.makedirs(_log_dir, exist_ok=True)
    except OSError:
        _log_dir = None

    root = logging.getLogger("studydesk")
    root.setLevel(logging.DEBUG)
    root.propagate = False

    if not root.handlers:
        formatter = logging.Formatter(_LOG_FORMAT, _DATE_FORMAT)
        if _log_dir:
            try:
                fh = RotatingFileHandler(
                    os.path.join(_log_dir, "studydesk.log"),
                    maxBytes=2_000_000,
                    backupCount=3,
                    encoding="utf-8",
                )
                fh.setLevel(logging.DEBUG)
                fh.setFormatter(formatter)
                root.addHandler(fh)
            except OSError:
                pass
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)
        root.addHandler(ch)

    _initialized = True
    return root


def get_logger(name="studydesk"):
    """Return a logger under the studydesk namespace."""
    if not _initialized:
        return logging.getLogger(name)
    return logging.getLogger(name)