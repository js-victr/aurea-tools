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
    "pt": "pt_BR",
    "pt_br": "pt_BR",
    "pt_BR": "pt_BR",
    "en": "en_US",
    "en_us": "en_US",
    "en_US": "en_US",
}


def _detect_system_locale() -> str:
    """Detect system locale and map to supported locale."""
    try:
        sys_locale = locale.getlocale()[0] or ""
    except Exception:
        sys_locale = ""

    # Check environment variables (common in Linux/Termux)
    for env_var in ("LANG", "LC_ALL", "LC_MESSAGES", "LANGUAGE"):
        val = os.environ.get(env_var, "")
        if val:
            sys_locale = val
            break

    sys_locale = sys_locale.split(".")[0]  # Remove encoding (e.g., .UTF-8)

    if sys_locale in SUPPORTED_LOCALES:
        return SUPPORTED_LOCALES[sys_locale]

    # Try language prefix (e.g., "pt" from "pt_BR")
    lang = sys_locale.split("_")[0].lower()
    if lang in SUPPORTED_LOCALES:
        return SUPPORTED_LOCALES[lang]

    return "en_US"


def _load_locale(locale_code: str) -> dict:
    """Load a locale JSON file."""
    filepath = _LOCALES_DIR / f"{locale_code}.json"
    if not filepath.exists():
        return {}
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def init(locale_override: str | None = None):
    """
    Initialize the i18n system.

    Args:
        locale_override: Force a specific locale (e.g., "pt", "en").
                        If None, auto-detects from system.
    """
    global _current_locale, _strings, _loaded

    if locale_override:
        key = locale_override.lower().replace("-", "_")
        _current_locale = SUPPORTED_LOCALES.get(key, "en_US")
    else:
        _current_locale = _detect_system_locale()

    _strings = _load_locale(_current_locale)

    # Fallback to en_US if strings are empty
    if not _strings and _current_locale != "en_US":
        _strings = _load_locale("en_US")
        _current_locale = "en_US"

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
