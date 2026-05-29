"""
aurea.core.config — Persistent configuration and user preferences manager.
"""

import json
import os
import sys
from pathlib import Path

_config_manager = None


class ConfigManager:
    """Manages reading and writing persistent configuration from a JSON file in user directory."""

    def __init__(self, filename: str = ".aureatools.json"):
        self.filename = filename
        self.config_path = self._get_config_path()
        self.preferences = {
            "locale": "pt_BR",
            "no_color": False,
            "default_netflow_port": 2055,
            "bgp_looking_glass_target": "8.8.8.0/24",
            "api_keys": {
                "shodan": "",
                "virustotal": "",
                "netbox": ""
            }
        }
        self.load()

    def _get_config_path(self) -> Path:
        """Locates the safe config file path depending on OS."""
        if sys.platform == "win32":
            base = Path(os.environ.get("USERPROFILE", Path.home()))
        else:
            base = Path.home()
        return base / self.filename

    def load(self):
        """Loads persistent JSON preferences, gracefully falling back to defaults on error."""
        if not self.config_path.exists():
            return
        
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    self.preferences.update(data)
        except Exception:
            pass  # Fail silent, retain defaults

    def save(self):
        """Saves current preferences dictionary to the configuration path."""
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.preferences, f, indent=4, ensure_ascii=False)
        except Exception:
            pass  # Fail silent (e.g. read-only system)

    def get(self, key: str, default=None):
        """Get a configuration preference value."""
        return self.preferences.get(key, default)

    def set(self, key: str, value):
        """Set a configuration preference and commit/save immediately."""
        self.preferences[key] = value
        self.save()

    def get_api_key(self, service: str) -> str:
        """Get an API key for a specific service."""
        keys = self.preferences.get("api_keys", {})
        return keys.get(service, "")

    def set_api_key(self, service: str, key: str):
        """Set an API key for a specific service and save."""
        if "api_keys" not in self.preferences:
            self.preferences["api_keys"] = {}
        self.preferences["api_keys"][service] = key
        self.save()


def get_instance() -> ConfigManager:
    """Singleton getter for the global configuration manager."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager
