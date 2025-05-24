"""
IP filtering functionality for PyWebGuard with both sync and async support.
"""

from typing import Dict, List, Optional, Union, Any
import ipaddress
from pywebguard.core.config import IPFilterConfig
from pywebguard.storage.base import BaseStorage, AsyncBaseStorage
from pywebguard.filters.base import BaseFilter, AsyncBaseFilter


class IPFilter(BaseFilter):
    """
    Filter requests based on IP addresses (synchronous).
    """

    def __init__(
        self,
        config: IPFilterConfig,
        storage: BaseStorage,
    ):
        """
        Initialize the IP filter.

        Args:
            config: IP filter configuration
            storage: Storage backend for persistent data
        """
        self.config = config
        self.storage = storage

        # Parse IP networks for efficient matching
        self.whitelist_networks = self._parse_ip_networks(config.whitelist)
        self.blacklist_networks = self._parse_ip_networks(config.blacklist)

    def _parse_ip_networks(self, ip_list: List[str]) -> List:
        """
        Parse IP addresses and CIDR ranges into network objects.

        Args:
            ip_list: List of IP addresses and CIDR ranges

        Returns:
            List of network objects
        """
        networks = []
        for ip in ip_list:
            try:
                # Handle CIDR notation
                if "/" in ip:
                    networks.append(ipaddress.ip_network(ip, strict=False))
                else:
                    # Convert single IP to network with /32 or /128 mask
                    networks.append(ipaddress.ip_address(ip))
            except ValueError:
                # Log invalid IP address
                pass
        return networks

    def is_allowed(self, ip_address: str) -> Dict[str, Union[bool, str]]:
        """
        Check if an IP address is allowed.

        Args:
            ip_address: The IP address to check

        Returns:
            Dict with allowed status and reason
        """
        if not self.config.enabled:
            return {"allowed": True, "reason": ""}

        # Re-parse networks in case config changed at runtime
        self.whitelist_networks = self._parse_ip_networks(self.config.whitelist)
        self.blacklist_networks = self._parse_ip_networks(self.config.blacklist)

        try:
            ip = ipaddress.ip_address(ip_address)

            # Check if IP is banned (highest priority)
            if self.storage.exists(f"banned_ip:{ip_address}"):
                return {"allowed": False, "reason": "IP is banned"}

            # Check if IP is in blacklist (second priority)
            if self._is_ip_in_networks(ip, self.blacklist_networks):
                return {"allowed": False, "reason": "IP in blacklist"}

            # Check if IP is in whitelist (lowest priority)
            if self.whitelist_networks and not self._is_ip_in_networks(
                ip, self.whitelist_networks
            ):
                return {"allowed": False, "reason": "IP not in whitelist"}

            # Additional checks for cloud providers, geolocation, etc. would go here

            return {"allowed": True, "reason": ""}

        except ValueError:
            # Invalid IP address
            return {"allowed": False, "reason": "Invalid IP address"}

    def _is_ip_in_networks(self, ip, networks) -> bool:
        """
        Check if an IP is in a list of networks.

        Args:
            ip: IP address to check
            networks: List of networks to check against

        Returns:
            True if IP is in any network, False otherwise
        """
        for network in networks:
            if isinstance(network, ipaddress.IPv4Network) or isinstance(
                network, ipaddress.IPv6Network
            ):
                if ip in network:
                    return True
            elif ip == network:  # Direct comparison for single IP addresses
                return True
        return False


class AsyncIPFilter(AsyncBaseFilter):
    """
    Filter requests based on IP addresses (asynchronous).
    """

    def __init__(
        self,
        config: IPFilterConfig,
        storage: AsyncBaseStorage,
    ):
        """
        Initialize the async IP filter.

        Args:
            config: IP filter configuration
            storage: Async storage backend for persistent data
        """
        self.config = config
        self.storage = storage

        # Parse IP networks for efficient matching
        self.whitelist_networks = self._parse_ip_networks(config.whitelist)
        self.blacklist_networks = self._parse_ip_networks(config.blacklist)

    def _parse_ip_networks(self, ip_list: List[str]) -> List:
        """
        Parse IP addresses and CIDR ranges into network objects.

        Args:
            ip_list: List of IP addresses and CIDR ranges

        Returns:
            List of network objects
        """
        networks = []
        for ip in ip_list:
            try:
                # Handle CIDR notation
                if "/" in ip:
                    networks.append(ipaddress.ip_network(ip, strict=False))
                else:
                    # Convert single IP to network with /32 or /128 mask
                    networks.append(ipaddress.ip_address(ip))
            except ValueError:
                # Log invalid IP address
                pass
        return networks

    async def is_allowed(self, ip_address: str) -> Dict[str, Union[bool, str]]:
        """
        Check if an IP address is allowed asynchronously.

        Args:
            ip_address: The IP address to check

        Returns:
            Dict with allowed status and reason
        """
        if not self.config.enabled:
            return {"allowed": True, "reason": ""}

        # Re-parse networks in case config changed at runtime
        self.whitelist_networks = self._parse_ip_networks(self.config.whitelist)
        self.blacklist_networks = self._parse_ip_networks(self.config.blacklist)

        try:
            ip = ipaddress.ip_address(ip_address)

            # Check if IP is banned (highest priority)
            if await self.storage.exists(f"banned_ip:{ip_address}"):
                return {"allowed": False, "reason": "IP is banned"}

            # Check if IP is in blacklist (second priority)
            if self._is_ip_in_networks(ip, self.blacklist_networks):
                return {"allowed": False, "reason": "IP in blacklist"}

            # Check if IP is in whitelist (lowest priority)
            if self.whitelist_networks and not self._is_ip_in_networks(
                ip, self.whitelist_networks
            ):
                return {"allowed": False, "reason": "IP not in whitelist"}

            # Additional checks for cloud providers, geolocation, etc. would go here

            return {"allowed": True, "reason": ""}

        except ValueError:
            # Invalid IP address
            return {"allowed": False, "reason": "Invalid IP address"}

    def _is_ip_in_networks(self, ip, networks) -> bool:
        """
        Check if an IP is in a list of networks.

        Args:
            ip: IP address to check
            networks: List of networks to check against

        Returns:
            True if IP is in any network, False otherwise
        """
        for network in networks:
            if isinstance(network, ipaddress.IPv4Network) or isinstance(
                network, ipaddress.IPv6Network
            ):
                if ip in network:
                    return True
            elif ip == network:  # Direct comparison for single IP addresses
                return True
        return False
