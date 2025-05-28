"""
Penetration detection functionality for PyWebGuard with both sync and async support.
"""

from typing import Dict, Any, List
import re
from pywebguard.core.config import PenetrationDetectionConfig
from pywebguard.storage.base import BaseStorage, AsyncBaseStorage
from pywebguard.security.base import BaseSecurityComponent, AsyncBaseSecurityComponent


class PenetrationDetector(BaseSecurityComponent):
    """
    Detect potential penetration attempts (synchronous).
    """

    def __init__(
        self,
        config: PenetrationDetectionConfig,
        storage: BaseStorage,
    ):
        """
        Initialize the penetration detector.

        Args:
            config: Penetration detection configuration
            storage: Storage backend for persistent data
        """
        self.config = config
        self.storage = storage

        # Compile patterns for efficient matching
        self.patterns = self._compile_patterns()

    def _compile_patterns(self) -> List[re.Pattern]:
        """
        Compile regex patterns for efficient matching.

        Returns:
            List of compiled regex patterns
        """
        patterns = []

        for pattern in self.config.suspicious_patterns:
            try:
                patterns.append(re.compile(pattern))
            except re.error:
                # Log invalid pattern
                pass

        return patterns

    def check_request(self, request_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if a request contains suspicious patterns.

        Args:
            request_info: Dict with request information

        Returns:
            Dict with allowed status and reason
        """
        if not self.config.enabled:
            return {"allowed": True, "reason": ""}

        # Check path for suspicious patterns
        path = request_info.get("path", "")
        if self._check_suspicious_patterns(path):
            return {"allowed": False, "reason": "Suspicious path detected"}

        # Check query parameters for suspicious patterns
        query = request_info.get("query", {})
        for key, value in query.items():
            if self._check_suspicious_patterns(key) or self._check_suspicious_patterns(
                value
            ):
                return {
                    "allowed": False,
                    "reason": "Suspicious query parameter detected",
                }

        # Check headers for suspicious patterns
        headers = request_info.get("headers", {})
        for key, value in headers.items():
            # Skip common headers
            if key.lower() in [
                "user-agent",
                "accept",
                "accept-language",
                "accept-encoding",
                "connection",
            ]:
                continue

            if self._check_suspicious_patterns(key) or self._check_suspicious_patterns(
                value
            ):
                return {"allowed": False, "reason": "Suspicious header detected"}

        return {"allowed": True, "reason": ""}

    def _check_suspicious_patterns(self, text: Any) -> bool:
        """
        Check if a text contains suspicious patterns.

        Args:
            text: The text to check

        Returns:
            True if suspicious patterns are found, False otherwise
        """
        if not text:
            return False

        # Convert to string if not already
        if not isinstance(text, str):
            text = str(text)

        # Check each pattern
        for pattern in self.patterns:
            if pattern.search(text):
                return True

        return False


class AsyncPenetrationDetector(AsyncBaseSecurityComponent):
    """
    Detect potential penetration attempts asynchronously.
    """

    def __init__(
        self,
        config: PenetrationDetectionConfig,
        storage: AsyncBaseStorage,
    ):
        """
        Initialize the penetration detector.

        Args:
            config: Penetration detection configuration
            storage: Async storage backend for persistent data
        """
        self.config = config
        self.storage = storage

        # Compile patterns for efficient matching
        self.patterns = self._compile_patterns()

    def _compile_patterns(self) -> List[re.Pattern]:
        """
        Compile regex patterns for efficient matching.

        Returns:
            List of compiled regex patterns
        """
        patterns = []

        for pattern in self.config.suspicious_patterns:
            try:
                patterns.append(re.compile(pattern))
            except re.error:
                # Log invalid pattern
                pass

        return patterns

    async def check_request(self, request_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if a request contains suspicious patterns asynchronously.

        Args:
            request_info: Dict with request information

        Returns:
            Dict with allowed status and reason
        """
        if not self.config.enabled:
            return {"allowed": True, "reason": ""}

        # Check path for suspicious patterns
        path = request_info.get("path", "")
        if self._check_suspicious_patterns(path):
            return {"allowed": False, "reason": "Suspicious path detected"}

        # Check query parameters for suspicious patterns
        query = request_info.get("query", {})
        for key, value in query.items():
            if self._check_suspicious_patterns(key) or self._check_suspicious_patterns(
                value
            ):
                return {
                    "allowed": False,
                    "reason": "Suspicious query parameter detected",
                }

        # Check headers for suspicious patterns
        headers = request_info.get("headers", {})
        for key, value in headers.items():
            # Skip common headers
            if key.lower() in [
                "user-agent",
                "accept",
                "accept-language",
                "accept-encoding",
                "connection",
            ]:
                continue

            if self._check_suspicious_patterns(key) or self._check_suspicious_patterns(
                value
            ):
                return {"allowed": False, "reason": "Suspicious header detected"}

        return {"allowed": True, "reason": ""}

    def _check_suspicious_patterns(self, text: Any) -> bool:
        """
        Check if a text contains suspicious patterns.

        Args:
            text: The text to check

        Returns:
            True if suspicious patterns are found, False otherwise
        """
        if not text:
            return False

        # Convert to string if not already
        if not isinstance(text, str):
            text = str(text)

        # Check each pattern
        for pattern in self.patterns:
            if pattern.search(text):
                return True

        return False
