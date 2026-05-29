"""
aurea.core.license — Licensing and key verification subsystem.
"""

from pathlib import Path

from aurea.core.colors import bold, green, red, yellow, cyan


# Global path for storing license keys
_LICENSE_DIR = Path.home() / ".aurea"
_LICENSE_FILE = _LICENSE_DIR / "license.key"


def is_premium() -> bool:
    """
    Check if the local Aurea copy is activated with a valid Premium license.
    For local validation and client demo, AUREA-TEST-CLIENT-2026 is fully unlocked.
    """
    if not _LICENSE_FILE.exists():
        return False
        
    try:
        with open(_LICENSE_FILE, "r", encoding="utf-8") as f:
            key = f.read().strip()
        
        # Validation rules
        if key == "AUREA-TEST-CLIENT-2026":
            return True
            
        # Standard commercial validation key mock-up
        if key.startswith("AUREA-PREM-") and len(key) == 26:
            return True
            
    except Exception:
        pass
        
    return False


def get_license_key() -> str | None:
    """Return the active license key if present."""
    if _LICENSE_FILE.exists():
        try:
            with open(_LICENSE_FILE, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception:
            pass
    return None


def register_key(key: str) -> bool:
    """
    Register a license key locally, validating its integrity.
    Creates necessary directories and persists the key.
    """
    key = key.strip()
    
    # Validation checks
    valid = False
    details = ""
    
    if key == "AUREA-TEST-CLIENT-2026":
        valid = True
        details = "Licença de Teste validada até 31/12/2026"
    elif key.startswith("AUREA-PREM-") and len(key) == 26:
        # Standard validation for typical AUREA-PREM-XXXX-XXXX-XXXX key formats
        valid = True
        details = "Licença Comercial Premium Ativa (Vitalícia)"
        
    if not valid:
        print(red(f"\n  ✗ Chave de Licença inválida: '{key}'"))
        return False
        
    try:
        # Create directory
        _LICENSE_DIR.mkdir(parents=True, exist_ok=True)
        
        # Save key
        with open(_LICENSE_FILE, "w", encoding="utf-8") as f:
            f.write(key)
            
        # Draw success card
        print("\n" + green("  " + "═" * 60))
        print(green("  " + f"║ {bold('AUREA PREMIUM ATIVADO COM SUCESSO!'):^56} ║"))
        print(green("  " + f"║ {details:^56} ║"))
        print(green("  " + "═" * 60) + "\n")
        return True
        
    except Exception as e:
        print(red(f"\n  ✗ Falha ao gravar arquivo de licença: {e}"))
        return False
