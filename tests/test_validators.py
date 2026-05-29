"""
Unit tests for input validators.
"""

import unittest
from aurea.core import validators


class TestValidators(unittest.TestCase):

    def test_validate_ip(self):
        self.assertEqual(validators.validate_ip("1.1.1.1"), "1.1.1.1")
        self.assertEqual(validators.validate_ip("2001:4860:4860::8888"), "2001:4860:4860::8888")
        with self.assertRaises(ValueError):
            validators.validate_ip("invalid-ip")
        with self.assertRaises(ValueError):
            validators.validate_ip("")

    def test_validate_domain(self):
        self.assertEqual(validators.validate_domain("google.com"), "google.com")
        self.assertEqual(validators.validate_domain("SUB.DOMAIN.CO.UK"), "sub.domain.co.uk")
        with self.assertRaises(ValueError):
            validators.validate_domain("invalid_domain")
        with self.assertRaises(ValueError):
            validators.validate_domain("dom")

    def test_validate_port(self):
        self.assertEqual(validators.validate_port("80"), 80)
        self.assertEqual(validators.validate_port("  443  "), 443)
        with self.assertRaises(ValueError):
            validators.validate_port("0")
        with self.assertRaises(ValueError):
            validators.validate_port("65536")
        with self.assertRaises(ValueError):
            validators.validate_port("abc")

    def test_validate_mac(self):
        self.assertEqual(validators.validate_mac("00:1A:2B:3C:4D:5E"), "00:1A:2B:3C:4D:5E")
        self.assertEqual(validators.validate_mac("00-1A-2B-3C-4D-5E"), "00:1A:2B:3C:4D:5E")
        with self.assertRaises(ValueError):
            validators.validate_mac("invalid-mac")

    def test_validate_cidr(self):
        self.assertEqual(validators.validate_cidr("192.168.0.0/24"), "192.168.0.0/24")
        self.assertEqual(validators.validate_cidr("10.0.0.1"), "10.0.0.0/24")  # Default mask added
        with self.assertRaises(ValueError):
            validators.validate_cidr("invalid-cidr")

    def test_validate_asn(self):
        self.assertEqual(validators.validate_asn("AS12345"), "12345")
        self.assertEqual(validators.validate_asn("12345"), "12345")
        self.assertEqual(validators.validate_asn("  as54321  "), "54321")
        with self.assertRaises(ValueError):
            validators.validate_asn("invalid")


if __name__ == "__main__":
    unittest.main()
