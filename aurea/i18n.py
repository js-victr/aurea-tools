"""
aurea.i18n — Internationalization system

Provides the t() function for translating UI strings.
Supports PT-BR and EN-US with auto-detection from system locale.
"""

import json
import locale
import os
from pathlib import Path

_LOCALES_DIR = Path(__file__).parent / "locales"
_current_locale: str = "en_US"
_strings: dict = {}
_loaded: bool = False

SUPPORTED_LOCALES = {
    "en": "en_US",
    "en_us": "en_US",
    "en_US": "en_US",
}


def _detect_system_locale() -> str:
    return "en_US"


def _load_locale(locale_code: str) -> dict:
    """Load a locale JSON file."""
    filepath = _LOCALES_DIR / "en_US.json"
    if not filepath.exists():
        return {}
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def init(locale_override: str | None = None):
    """Initialize the i18n system in English only."""
    global _current_locale, _strings, _loaded
    _current_locale = "en_US"
    _strings = _load_locale("en_US")
    _loaded = True


def get_locale() -> str:
    """Return the current active locale code."""
    if not _loaded:
        init()
    return _current_locale


def t(key: str, **kwargs) -> str:
    """
    Translate a key to the current locale.

    Supports nested keys with dot notation: t("menu.exit")
    Supports format arguments: t("tool.testing", target="8.8.8.8")

    Args:
        key: Dot-separated key path (e.g., "menu.exit", "tools.ping.title")
        **kwargs: Format arguments to interpolate into the string.

    Returns:
        Translated string, or the key itself if not found.
    """
    if not _loaded:
        init()

    # Navigate nested dict with dot notation
    parts = key.split(".")
    current = _strings
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return key  # Key not found → return key as fallback

    if not isinstance(current, str):
        return key

    # Interpolate format arguments
    if kwargs:
        try:
            return current.format(**kwargs)
        except (KeyError, IndexError):
            return current

    return current
