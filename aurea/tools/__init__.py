"""
aurea.tools — Tool registry and decorator system.

Each tool is registered via the @tool decorator with metadata.
The CLI reads from this registry to build menus and dispatch commands.
"""

from dataclasses import dataclass, field
from typing import Callable

# --- Tool metadata ---

@dataclass
class ToolInfo:
    """Metadata for a registered tool."""
    number: str
    name: str
    category: str
    keywords: list[str] = field(default_factory=list)
    tier: str = "free"  # "free" or "premium"
    func: Callable | None = None
    i18n_key: str = ""  # Key for translated name, e.g., "tools.ping.name"
    parameters: list[dict] = field(default_factory=list)


# --- Global registry ---

_registry: dict[str, ToolInfo] = {}

# Category definitions (order matters for menu display)
CATEGORIES = [
    ("diagnostics", "tools.cat.diagnostics"),
    ("services", "tools.cat.services"),
    ("bgp", "tools.cat.bgp"),
    ("automation", "tools.cat.automation"),
]


def tool(
    number: str,
    name: str,
    category: str,
    *,
    keywords: list[str] | None = None,
    tier: str = "free",
    i18n_key: str = "",
    parameters: list[dict] | None = None,
):
    """
    Decorator to register a function as an Aurea tool.

    Usage:
        @tool("1", "Local IP & Interfaces", "diagnostics",
              keywords=["ip", "local", "interface"], tier="free")
        def info_local_network():
            ...
    """
    def decorator(func: Callable) -> Callable:
        import functools
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            from aurea.i18n import get_locale, t
            from aurea.core.colors import bold, green, yellow, cyan, dim
            from aurea.tools.descriptions import TOOL_GUIDES
            
            # 1. Look up description and usage
            guide = TOOL_GUIDES.get(number, {})
            locale = get_locale() or "pt_BR"
            lang = "pt" if locale.startswith("pt") else "en"
            
            guide_lang = guide.get(lang, guide.get("pt", {}))
            desc = guide_lang.get("desc", "")
            use = guide_lang.get("use", "")
            
            # 2. Print beautiful manual/guide box
            if desc or use:
                print(cyan("\n┌" + "─" * 78 + "┐"))
                
                def print_wrapped_line(colored_lbl: str, lbl_len: int, text: str):
                    max_text_width = 72 - lbl_len
                    
                    import textwrap
                    wrapped_lines = textwrap.wrap(text, width=max_text_width)
                    
                    for i, line in enumerate(wrapped_lines):
                        if i == 0:
                            padded_line = f"{line:<{max_text_width}}"
                            print(f"{cyan('│')} {colored_lbl}: {padded_line} {cyan('│')}")
                        else:
                            indent = " " * (lbl_len + 2)
                            padded_line = f"{indent}{line:<{max_text_width}}"
                            print(f"{cyan('│')} {padded_line} {cyan('│')}")

                if desc:
                    desc_lbl = "PROPÓSITO" if lang == "pt" else "PURPOSE"
                    print_wrapped_line(bold(green(desc_lbl)), len(desc_lbl), desc)
                if use:
                    use_lbl = "COMO USAR" if lang == "pt" else "HOW TO USE"
                    print_wrapped_line(bold(yellow(use_lbl)), len(use_lbl), use)
                    
                print(cyan("└" + "─" * 78 + "┘\n"))
                
            # 3. Print verbose status
            from aurea.core.ui import verbose
            verbose(f"Iniciando ferramenta #{number}: {name} ({category})")
            verbose("Carregando subsistemas do Core, cores ANSI e verificando chaves de API...")
            
            # 4. Call actual tool function
            return func(*args, **kwargs)
            
        info = ToolInfo(
            number=number,
            name=name,
            category=category,
            keywords=keywords or [],
            tier=tier,
            func=wrapper,
            i18n_key=i18n_key or f"tools.{func.__name__}.name",
            parameters=parameters or [],
        )
        _registry[number] = info
        # Store metadata on the wrapper for introspection
        wrapper._tool_info = info
        return wrapper
    return decorator


def get_tool(number: str) -> ToolInfo | None:
    """Get a tool by its number."""
    return _registry.get(number)


def get_all_tools() -> list[ToolInfo]:
    """Get all registered tools, sorted by number."""
    return sorted(_registry.values(), key=lambda t: int(t.number))


def get_tools_by_category(category: str) -> list[ToolInfo]:
    """Get all tools in a category, sorted by number."""
    return sorted(
        [t for t in _registry.values() if t.category == category],
        key=lambda t: int(t.number),
    )


def search_tools(query: str) -> list[ToolInfo]:
    """Search tools by name, number, or keywords."""
    q = query.lower()
    results = []
    for info in _registry.values():
        if (
            q == info.number
            or q in info.name.lower()
            or any(q == kw for kw in info.keywords)
        ):
            results.append(info)
    return sorted(results, key=lambda t: int(t.number))


# --- Auto-import tools when this package is imported ---

_loaded = False


def _load_all_tools():
    """Import all tool modules dynamically to trigger @tool registration."""
    global _loaded
    if _loaded:
        return
    import pkgutil
    import importlib
    import sys
    
    package = sys.modules[__name__]
    for _, module_name, is_pkg in pkgutil.iter_modules(package.__path__):
        if not is_pkg and module_name != "__init__":
            importlib.import_module(f"{__name__}.{module_name}")
    _loaded = True

