"""
aurea.core.ui — Terminal UI components: headers, input, pause, banner.
"""

import shutil
import subprocess
import sys
import platform
from collections import deque

from aurea import __version__
from aurea.i18n import t
from aurea.core.colors import blue, green, red, yellow, cyan, bold, dim
from aurea.core import platform_info
from aurea.core.platform_info import clear_screen, is_windows

# --- History ---
_history: deque = deque(maxlen=5)


def record_usage(option: str):
    """Record a tool usage in history."""
    _history.appendleft(option)


def get_history() -> deque:
    return _history


# --- Terminal interaction ---

# --- Thread-Local Web Redirection ---
import threading

web_context = threading.local()

def pause():
    """Pause and wait for ENTER, bypassing if inside web execution thread."""
    if getattr(web_context, "active", False):
        return
    input(f"\n{cyan(t('ui.press_enter'))}")


def input_with_default(message: str, default: str = "") -> str:
    """Prompt the user with an optional default value, pulling from web variables if active."""
    if getattr(web_context, "active", False):
        # Pull parameter from inputs dict matching name keywords
        inputs_dict = getattr(web_context, "inputs", {})
        msg_lower = message.lower()
        
        # Mapping common keywords
        for key, val in inputs_dict.items():
            k_low = key.lower()
            if k_low in msg_lower:
                return str(val)
            # Smart synonyms for multi-vendor and localized prompts
            if k_low == "target" and ("alvo" in msg_lower or "host" in msg_lower or "ip" in msg_lower or "destino" in msg_lower or "domain" in msg_lower or "url" in msg_lower or "site" in msg_lower or "enter_ip" in msg_lower):
                return str(val)
            if k_low == "port" and ("port" in msg_lower or "porta" in msg_lower):
                return str(val)
            if k_low == "count" and ("count" in msg_lower or "pacotes" in msg_lower or "quantidade" in msg_lower):
                return str(val)
            if k_low == "cidr" and ("cidr" in msg_lower or "sub-rede" in msg_lower or "faixa" in msg_lower or "rede" in msg_lower):
                return str(val)
            if k_low == "login" and ("login" in msg_lower or "usuário" in msg_lower or "user" in msg_lower or "conexão" in msg_lower):
                return str(val)
            if k_low == "password" and ("senha" in msg_lower or "pass" in msg_lower or "password" in msg_lower):
                return str(val)
            if k_low == "domain" and ("domain" in msg_lower or "domínio" in msg_lower or "host" in msg_lower or "alvo" in msg_lower or "site" in msg_lower):
                return str(val)
            if k_low == "prefixes" and ("prefixes" in msg_lower or "redes" in msg_lower or "cidr" in msg_lower or "faixa" in msg_lower):
                return str(val)
            if k_low == "asn" and ("asn" in msg_lower or "sistema autônomo" in msg_lower):
                return str(val)
            if k_low == "community" and ("community" in msg_lower or "comunidade" in msg_lower):
                return str(val)
            if k_low == "length" and ("length" in msg_lower or "comprimento" in msg_lower or "tamanho" in msg_lower or "duração" in msg_lower):
                return str(val)
            if k_low == "vlan" and ("vlan" in msg_lower or "id" in msg_lower):
                return str(val)
                
        # Queue fallback
        queue = getattr(web_context, "queue", [])
        if queue:
            return str(queue.pop(0))
        return default

    prompt = f"{yellow(message)}"
    if default:
        prompt += f" {dim('[' + t('ui.default') + ': ' + default + ']')}"
    prompt += f"{yellow(': ')}"
    try:
        entry = input(prompt).strip()
        return entry if entry else default
    except (EOFError, KeyboardInterrupt):
        return default



def run_command_safe(command: list[str]) -> subprocess.CompletedProcess | None:
    """Run a subprocess safely, capturing output, with cross-platform fallbacks and logging."""
    from aurea.core.process import CommandRunner
    return CommandRunner.run(command)


def header(title: str):
    """Display the Aurea-styled header with a title."""
    clear_screen()
    prefix_len = 21  # "  :: A U R E A ::  | "
    inner_width = max(60, prefix_len + len(title) + 2)
    title_space = inner_width - prefix_len

    top = "╔" + "═" * inner_width + "╗"
    bottom = "╚" + "═" * inner_width + "╝"

    print(cyan(top))
    print(f"{cyan('║')}  {yellow(':: A U R E A ::')}  {cyan('|')} {green(f'{title:^{title_space}}')}{cyan('║')}")
    print(cyan(bottom) + "\n")


def show_banner():
    """Display the Aurea modern 3D ASCII art banner & status cards."""
    print(cyan(r"   █████╗ ██╗   ██╗██████╗ ███████╗ █████╗ "))
    print(cyan(r"  ██╔══██╗██║   ██║██╔══██╗██╔════╝██╔══██╗"))
    print(cyan(r"  ███████║██║   ██║██████╔╝█████╗  ███████║"))
    print(cyan(r"  ██╔══██║██║   ██║██╔══██╗██╔══╝  ██╔══██║"))
    print(cyan(r"  ██║  ██║╚██████╔╝██║  ██║███████╗██║  ██║"))
    print(cyan(r"  ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝"))
    
    width = max(platform_info.terminal_width(), 40)
    top_len = min(width - 4, 76)
    top_line = "═" * top_len
    
    print(cyan(f" ╔{top_line}╗"))
    title_line = f" A U R E A   T O O L S   —   v{__version__}  (Carrier-Grade NOC System)"
    print(f" {cyan('║')} {yellow(f'{title_line:<{top_len - 2}}')} {cyan('║')}")
    
    contrib_line = "Contribute: https://github.com/js-victr/aurea-tools"
    print(f" {cyan('║')} {dim(f'{contrib_line:<{top_len - 2}}')} {cyan('║')}")
    
    sys_info = f"{platform.system()} {platform.release()} | Python {platform.python_version()}"
    sys_line = f"{t('ui.system')}: {sys_info}"
    print(f" {cyan('║')} {dim(f'{sys_line:<{top_len - 2}}')} {cyan('║')}")
    print(cyan(f" ╚{top_line}╝"))


# --- stdin protection for fileless execution ---

def protect_stdin():
    """Reopen stdin for fileless execution (curl | python)."""
    if not sys.stdin.isatty():
        try:
            sys.stdin = open("CON" if is_windows() else "/dev/tty", "r")
        except Exception:
            pass


# --- Configure stdout to safely replace unencodable characters (common in Windows cmd/CP1252) ---
import sys
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass


def is_cancelled() -> bool:
    """Check if the execution was cancelled (stub for CLI compatibility)."""
    return False


def run_command_stream(command: list[str]):
    """Execute a native command streaming stdout/stderr line-by-line in real-time."""
    from aurea.core.process import CommandRunner
    for line in CommandRunner.run_stream(command):
        sys.stdout.write(line)
        sys.stdout.flush()


def verbose(message: str):
    """Print a highly detailed behind-the-scenes log message."""
    from aurea.core.colors import dim
    from aurea.i18n import get_locale
    locale = get_locale() or "pt_BR"
    tag = "BASTIDORES" if locale.startswith("pt") else "BEHIND-THE-SCENES"
    print(f"  {dim(f'⚙️  [{tag}]')} {dim(message)}")

