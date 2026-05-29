"""
aurea.core.validators — Input validation utilities.

All validators raise ValueError with a descriptive message on invalid input.
"""

import ipaddress
import re


def validate_ip(value: str) -> str:
    """
    Validate an IPv4 or IPv6 address.

    Returns the normalized IP string.
    Raises ValueError if invalid.
    """
    value = value.strip()
    if not value:
        raise ValueError("IP address cannot be empty")
    try:
        return str(ipaddress.ip_address(value))
    except ValueError:
        raise ValueError(f"Invalid IP address: {value!r}")


def validate_domain(value: str) -> str:
    """
    Validate a domain name.

    Returns the lowercase domain.
    Raises ValueError if invalid.
    """
    value = value.strip().lower()
    if not value:
        raise ValueError("Domain cannot be empty")

    # Basic domain regex: allows letters, digits, hyphens, dots
    pattern = r'^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,}$'
    if not re.match(pattern, value):
        raise ValueError(f"Invalid domain: {value!r}")
    return value


def validate_host(value: str) -> str:
    """
    Validate a host — either an IP address or a domain name.

    Returns the normalized value.
    """
    value = value.strip()
    if not value:
        raise ValueError("Host cannot be empty")
    try:
        return validate_ip(value)
    except ValueError:
        return validate_domain(value)


def validate_port(value: str) -> int:
    """
    Validate a TCP/UDP port number (1-65535).

    Returns the port as int.
    Raises ValueError if invalid.
    """
    value = value.strip()
    try:
        port = int(value)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid port: {value!r} (must be a number)")

    if not (1 <= port <= 65535):
        raise ValueError(f"Port {port} out of range (1-65535)")
    return port


def validate_mac(value: str) -> str:
    """
    Validate a MAC address.

    Accepts formats: 00:1A:2B:3C:4D:5E or 00-1A-2B-3C-4D-5E
    Returns uppercase colon-separated MAC.
    Raises ValueError if invalid.
    """
    value = value.strip().upper().replace("-", ":")
    pattern = r'^([0-9A-F]{2}:){5}[0-9A-F]{2}$'
    if not re.match(pattern, value):
        raise ValueError(f"Invalid MAC address: {value!r}")
    return value


def validate_cidr(value: str) -> str:
    """
    Validate a CIDR network notation (e.g., 192.168.0.0/24).

    Returns the normalized network string.
    Raises ValueError if invalid.
    """
    value = value.strip()
    if not value:
        raise ValueError("CIDR notation cannot be empty")

    # Add default /24 if no mask provided
    if "/" not in value:
        value += "/24"

    try:
        network = ipaddress.ip_network(value, strict=False)
        return str(network)
    except ValueError:
        raise ValueError(f"Invalid CIDR notation: {value!r}")


def validate_asn(value: str) -> str:
    """
    Validate and normalize an ASN (Autonomous System Number).

    Accepts: "AS12345", "as12345", "12345"
    Returns the numeric part as a string (e.g., "12345").
    Raises ValueError if invalid.
    """
    value = value.strip()
    cleaned = re.sub(r'[^0-9]', '', value)
    if not cleaned:
        raise ValueError(f"Invalid ASN: {value!r}")
    return cleaned


def validate_url(value: str) -> str:
    """
    Validate and normalize a URL.

    Prepends https:// if no scheme is provided.
    Returns the URL string.
    """
    value = value.strip()
    if not value:
        raise ValueError("URL cannot be empty")
    if not value.startswith(("http://", "https://")):
        value = "https://" + value
    return value
