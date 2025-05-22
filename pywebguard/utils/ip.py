"""
IP address utilities for PyWebGuard.
"""

import ipaddress
from typing import List, Dict, Any, Optional, Union


def is_valid_ip(ip: str) -> bool:
    """
    Check if a string is a valid IP address.

    Args:
        ip: The IP address to check

    Returns:
        True if valid, False otherwise
    """
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def is_valid_cidr(cidr: str) -> bool:
    """
    Check if a string is a valid CIDR range.

    Args:
        cidr: The CIDR range to check

    Returns:
        True if valid, False otherwise
    """
    try:
        ipaddress.ip_network(cidr, strict=False)
        return True
    except ValueError:
        return False


def get_real_ip(headers: Dict[str, str], remote_addr: str) -> str:
    """
    Get the real IP address from request headers.

    Args:
        headers: Request headers
        remote_addr: Remote address from the request

    Returns:
        The real IP address
    """
    # Check X-Forwarded-For header
    forwarded_for = headers.get("X-Forwarded-For")
    if forwarded_for:
        # Get the first IP in the list
        ip = forwarded_for.split(",")[0].strip()
        if is_valid_ip(ip):
            return ip

    # Check other common headers
    for header in ["X-Real-IP", "CF-Connecting-IP", "True-Client-IP"]:
        ip = headers.get(header)
        if ip and is_valid_ip(ip):
            return ip

    # Fall back to remote_addr
    return remote_addr


def is_cloud_provider_ip(ip: str) -> Dict[str, Any]:
    """
    Check if an IP belongs to a cloud provider.

    Args:
        ip: The IP address to check

    Returns:
        Dict with result and provider name if detected
    """
    # This is a placeholder for actual cloud provider IP detection
    # In a real implementation, this would check against lists of cloud provider IP ranges
    return {"is_cloud": False, "provider": None}
