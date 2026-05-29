"""
aurea.core.colors — ANSI color system with --no-color support.
"""

import os

# Global flag to disable colors (set via --no-color or NO_COLOR env)
_no_color: bool = False


def init(no_color: bool = False):
    """Initialize the color system."""
    global _no_color
    _no_color = no_color or os.environ.get("NO_COLOR", "") != ""


# ANSI escape codes
_CODES = {
    "blue":    "\033[94m",
    "green":   "\033[92m",
    "red":     "\033[91m",
    "yellow":  "\033[93m",
    "cyan":    "\033[96m",
    "bold":    "\033[1m",
    "dim":     "\033[2m",
    "reset":   "\033[0m",
}


def _wrap(code_name: str, text: str) -> str:
    """Wrap text with an ANSI color code."""
    if _no_color:
        return str(text)
    return f"{_CODES[code_name]}{text}{_CODES['reset']}"


def blue(text: str) -> str:
    return _wrap("blue", text)


def green(text: str) -> str:
    return _wrap("green", text)


def red(text: str) -> str:
    return _wrap("red", text)


def yellow(text: str) -> str:
    return _wrap("yellow", text)


def cyan(text: str) -> str:
    return _wrap("cyan", text)


def bold(text: str) -> str:
    return _wrap("bold", text)


def dim(text: str) -> str:
    return _wrap("dim", text)


# Raw codes for direct use (e.g., in f-strings that need partial coloring)
def raw(code_name: str) -> str:
    """Return raw ANSI code, or empty string if colors disabled."""
    if _no_color:
        return ""
    return _CODES.get(code_name, "")


# Convenience constants (lazy — respect _no_color at call time)
class C:
    """Namespace for raw ANSI codes. Use C.BLUE etc. in f-strings."""




    @property
    def BLUE(self) -> str:
        return raw("blue")

    @property
    def GREEN(self) -> str:
        return raw("green")

    @property
    def RED(self) -> str:
        return raw("red")

    @property
    def YELLOW(self) -> str:
        return raw("yellow")

    @property
    def CYAN(self) -> str:
        return raw("cyan")

    @property
    def BOLD(self) -> str:
        return raw("bold")

    @property
    def DIM(self) -> str:
        return raw("dim")

    @property
    def RESET(self) -> str:
        return raw("reset")


c = C()
