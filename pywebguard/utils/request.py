"""
Request parsing utilities for PyWebGuard.
"""

from typing import Dict, Any, Optional


def extract_request_info(request: Any) -> Dict[str, Any]:
    """
    Extract common information from a request object.
    This is a generic function that should be overridden by framework-specific implementations.

    Args:
        request: The framework-specific request object

    Returns:
        Dict with request information
    """
    # This is a placeholder that will be overridden
    return {
        "ip": "0.0.0.0",
        "user_agent": "",
        "method": "",
        "path": "",
        "query": {},
        "headers": {},
    }


def is_suspicious_request(request_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Check if a request is suspicious.

    Args:
        request_info: Dict with request information

    Returns:
        Dict with result and reason if suspicious
    """
    # This is a placeholder for actual suspicious request detection
    return {"suspicious": False, "reason": None}


def get_request_path(request: Any) -> str:
    """
    Get the path from a request object.
    This is a generic function that should be overridden by framework-specific implementations.

    Args:
        request: The framework-specific request object

    Returns:
        The request path
    """
    # Try common attributes for different frameworks
    if hasattr(request, "path") and request.path:
        return request.path

    if hasattr(request, "url") and hasattr(request.url, "path") and request.url.path:
        return request.url.path

    if hasattr(request, "path_info") and request.path_info:
        return request.path_info

    return ""
