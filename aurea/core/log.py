"""
aurea.core.log — Structured logging with file and console output.
"""

from __future__ import annotations

import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

_logger: logging.Logger | None = None
_log_dir: Path | None = None

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "module": record.module,
            "message": record.getMessage(),
        }
        if hasattr(record, "extra"):
            log_entry.update(record.extra)
        return json.dumps(log_entry, ensure_ascii=False)


def _get_log_dir() -> Path:
    """Get the log directory, creating it if needed."""
    global _log_dir
    if _log_dir is not None:
        return _log_dir

    # Default log locations per OS
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))

    _log_dir = base / "aurea" / "logs"
    _log_dir.mkdir(parents=True, exist_ok=True)
    return _log_dir


def init(*, verbose: bool = False, log_file: bool = True):
    """
    Initialize the logging system.

    Args:
        verbose: If True, set console level to DEBUG.
        log_file: If True, also log to a file.
    """
    global _logger
    if _logger is not None:
        return

    _logger = logging.getLogger("aurea")
    _logger.setLevel(logging.DEBUG)
    _logger.handlers.clear()

    # Console handler
    console = logging.StreamHandler(sys.stderr)
    console.setLevel(logging.DEBUG if verbose else logging.WARNING)
    console_fmt = logging.Formatter("[%(levelname)s] %(message)s")
    console.setFormatter(console_fmt)
    _logger.addHandler(console)

    # File handler
    if log_file:
        try:
            log_dir = _get_log_dir()
            date_str = datetime.now().strftime("%Y-%m-%d")
            log_path = log_dir / f"aurea_{date_str}.log"
            file_handler = logging.FileHandler(log_path, encoding="utf-8")
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(JSONFormatter())
            _logger.addHandler(file_handler)
        except Exception as e:
            print(f"Log init warning: {e}", file=sys.stderr)


def _ensure_init():
    if _logger is None:
        init()


def debug(msg: str, *args):
    _ensure_init()
    _logger.debug(msg, *args)


def info(msg: str, *args):
    _ensure_init()
    _logger.info(msg, *args)


def warning(msg: str, *args):
    _ensure_init()
    _logger.warning(msg, *args)


def error(msg: str, *args):
    _ensure_init()
    _logger.error(msg, *args)


def critical(msg: str, *args):
    _ensure_init()
    _logger.critical(msg, *args)
