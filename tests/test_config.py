# -*- coding: utf-8 -*-
"""
Unit tests for the AureaTools persistent ConfigManager system.
"""

import unittest
from pathlib import Path
from aurea.core.config import ConfigManager


class TestConfigManager(unittest.TestCase):

    def setUp(self):
        # Initialize ConfigManager with a unique temporary test file
        self.test_filename = ".aureatools_test_prefs.json"
        self.manager = ConfigManager(filename=self.test_filename)

    def tearDown(self):
        # Clean up the test config file if created
        if self.manager.config_path.exists():
            try:
                self.manager.config_path.unlink()
            except Exception:
                pass

    def test_default_preferences(self):
        self.assertEqual(self.manager.get("locale"), "pt_BR")
        self.assertEqual(self.manager.get("no_color"), False)
        self.assertEqual(self.manager.get("default_netflow_port"), 2055)

    def test_get_and_set_preferences(self):
        self.manager.set("locale", "en_US")
        self.assertEqual(self.manager.get("locale"), "en_US")
        
        # Test default fallback value
        self.assertEqual(self.manager.get("non_existent_key", "default_val"), "default_val")

    def test_persistence_between_instantiations(self):
        self.manager.set("locale", "en_US")
        self.manager.set("default_netflow_port", 9000)
        
        # Instantiate a new manager pointing to the same file
        new_manager = ConfigManager(filename=self.test_filename)
        self.assertEqual(new_manager.get("locale"), "en_US")
        self.assertEqual(new_manager.get("default_netflow_port"), 9000)


if __name__ == "__main__":
    unittest.main()
