"""
Unit tests for colors module.
"""

import unittest
from aurea.core import colors


class TestColors(unittest.TestCase):

    def setUp(self):
        colors.init(no_color=False)

    def test_colors_wrapping(self):
        self.assertIn("\033[94m", colors.blue("test"))
        self.assertIn("\033[92m", colors.green("test"))
        self.assertIn("\033[91m", colors.red("test"))
        self.assertIn("\033[93m", colors.yellow("test"))

    def test_no_color(self):
        colors.init(no_color=True)
        self.assertEqual("test", colors.blue("test"))
        self.assertEqual("test", colors.green("test"))
        self.assertEqual("test", colors.red("test"))
        self.assertEqual("", colors.raw("blue"))


if __name__ == "__main__":
    unittest.main()
