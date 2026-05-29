"""
Unit tests for internationalization system.
"""

import unittest
from aurea import i18n
from aurea.i18n import t


class TestI18n(unittest.TestCase):

    def setUp(self):
        # Force a fresh init with English
        i18n.init("en")

    def test_basic_translation(self):
        self.assertEqual(t("ui.press_enter"), "Press ENTER to return to menu...")
        self.assertEqual(t("ui.default"), "default")

    def test_nested_keys(self):
        self.assertEqual(t("tools.info_local_network.name"), "Local IP & Interfaces")

    def test_interpolation(self):
        self.assertEqual(
            t("tools.port_check.testing", host="127.0.0.1", port=80),
            "Testing TCP connection on 127.0.0.1:80..."
        )

    def test_fallback(self):
        # When key not found, it should return the key itself
        self.assertEqual(t("non.existent.key"), "non.existent.key")

    def test_pt_br_translation(self):
        i18n.init("pt")
        self.assertEqual(t("ui.press_enter"), "Pressione ENTER para voltar ao menu...")
        self.assertEqual(t("tools.info_local_network.name"), "IP Local & Interfaces")


if __name__ == "__main__":
    unittest.main()
