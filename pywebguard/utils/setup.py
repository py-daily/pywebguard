"""
Helpers for the short setup API (``FastAPIGuard.install`` / ``FlaskGuard.install``).

These functions turn flat options such as ``rate_limit="100/minute"`` into the
existing ``GuardConfig`` and ``route_rate_limits`` structures, so both
frameworks share one code path.
"""

import re
from typing import Any, Dict, List, Mapping, Optional, Union

from pywebguard.core.config import GuardConfig

_RATE_PATTERN = re.compile(r"^\s*(\d+)\s*/\s*(second|minute)\s*$", re.IGNORECASE)


def parse_rate(rate: str) -> int:
    """Convert a rate string such as ``"100/minute"`` to requests per minute.

    Args:
        rate: A string of the form ``"<count>/second"`` or ``"<count>/minute"``

    Returns:
        The equivalent number of requests per minute

    Raises:
        ValueError: If the string is malformed or the count is zero
    """
    match = _RATE_PATTERN.match(rate) if isinstance(rate, str) else None
    if match is None:
        raise ValueError(
            f"Invalid rate {rate!r}: expected '<count>/second' or '<count>/minute'"
        )
    count = int(match.group(1))
    if count < 1:
        raise ValueError(f"Invalid rate {rate!r}: count must be at least 1")
    return count * 60 if match.group(2).lower() == "second" else count


def route_limits_to_list(route_limits: Mapping[str, str]) -> List[Dict[str, Any]]:
    """Convert ``{"/api/x": "5/minute"}`` to the ``route_rate_limits`` list format.

    Burst is disabled so that a rate string means exactly that rate.
    """
    return [
        {
            "endpoint": endpoint,
            "requests_per_minute": parse_rate(rate),
            "burst_size": 0,
        }
        for endpoint, rate in route_limits.items()
    ]


def coerce_config(
    config: Optional[Union[GuardConfig, Dict[str, Any]]],
) -> Optional[GuardConfig]:
    """Validate a dict config into a ``GuardConfig``; pass anything else through."""
    if isinstance(config, dict):
        return GuardConfig.model_validate(config)
    return config


def build_install_config(
    config: Optional[Union[GuardConfig, Dict[str, Any]]] = None,
    rate_limit: Optional[str] = None,
    blocked_agents: Optional[List[str]] = None,
    ip_whitelist: Optional[List[str]] = None,
    ip_blacklist: Optional[List[str]] = None,
    cors_origins: Optional[List[str]] = None,
) -> GuardConfig:
    """Build the config used by ``install()``.

    Without ``config``, only rate limiting is on by default. IP filtering,
    user-agent filtering and CORS turn on only when their option is passed, and
    penetration detection stays off. A ``rate_limit`` string disables burst so it
    means exactly that rate. With ``config``, it is used as given and
    combining it with the flat options is an error.

    Raises:
        ValueError: If flat options are combined with ``config``, or a rate is invalid
    """
    flat = {
        "rate_limit": rate_limit,
        "blocked_agents": blocked_agents,
        "ip_whitelist": ip_whitelist,
        "ip_blacklist": ip_blacklist,
        "cors_origins": cors_origins,
    }
    passed = [name for name, value in flat.items() if value is not None]

    if config is not None:
        if passed:
            raise ValueError(
                f"Pass either config or the flat options, not both (got config and {', '.join(passed)})"
            )
        return coerce_config(config)

    rate_section: Dict[str, Any] = {}
    if rate_limit is not None:
        rate_section["requests_per_minute"] = parse_rate(rate_limit)
        rate_section["burst_size"] = 0

    return GuardConfig(
        rate_limit=rate_section,
        user_agent={
            "enabled": blocked_agents is not None,
            "blocked_agents": blocked_agents or [],
        },
        ip_filter={
            "enabled": ip_whitelist is not None or ip_blacklist is not None,
            "whitelist": ip_whitelist or [],
            "blacklist": ip_blacklist or [],
        },
        cors={
            "enabled": cors_origins is not None,
            **({"allow_origins": cors_origins} if cors_origins is not None else {}),
        },
        penetration={"enabled": False},
    )
