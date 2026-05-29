"""
aurea.core.platform_info — OS detection and environment awareness.
"""

import os
import platform
import shutil


def system() -> str:
    """Return the OS name: 'Windows', 'Linux', 'Darwin', etc."""
    return platform.system()


def is_windows() -> bool:
    return platform.system() == "Windows"


def is_linux() -> bool:
    return platform.system() == "Linux"


def is_macos() -> bool:
    return platform.system() == "Darwin"


def is_termux() -> bool:
    """Detect if running inside Termux on Android."""
    return "com.termux" in os.environ.get("PREFIX", "")


def terminal_width() -> int:
    """Return terminal width in columns."""
    return shutil.get_terminal_size().columns


def is_mobile() -> bool:
    """Return True if running on a mobile-sized terminal (Termux)."""
    return is_termux() or terminal_width() < 85


def system_info() -> str:
    """Return a formatted string with OS and Python version."""
    return f"{platform.system()} {platform.release()} | Python {platform.python_version()}"


def ping_count_flag() -> str:
    """Return the correct ping count flag for the current OS."""
    return "-n" if is_windows() else "-c"


def clear_screen():
    """Clear the terminal screen."""
    print("\033[2J\033[H", end="", flush=True)


def enable_ansi_windows():
    """Enable ANSI escape codes on Windows."""
    if not is_windows():
        return
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
        mode = ctypes.c_ulong()
        kernel32.GetConsoleMode(handle, ctypes.byref(mode))
        kernel32.SetConsoleMode(handle, mode.value | 0x0004)  # ENABLE_VIRTUAL_TERMINAL_PROCESSING
    except Exception:
        pass
