"""
Penetration detection functionality for PyWebGuard with both sync and async support.
"""

from typing import Dict, Any, List
import re
from pywebguard.core.config import PenetrationDetectionConfig
from pywebguard.storage.base import BaseStorage, AsyncBaseStorage
from pywebguard.security.base import BaseSecurityComponent, AsyncBaseSecurityComponent


SUSPICIOUS_PATTERNS = [
    r"(?i)(?:union\s+select|select\s+.*\s+from|insert\s+into|update\s+.*\s+set|delete\s+from)",  # SQL injection
    r"(?i)(?:<script>|javascript:|onerror=|onload=|eval\(|setTimeout\(|document\.cookie)",  # XSS
    r"(?i)(?:\.\.\/|\.\.\\|\/etc\/passwd|\/bin\/bash|cmd\.exe|command\.com)",  # Path traversal
    r"(?i)(?:\/wp-admin|\/wp-login|\/administrator|\/admin|\/phpmyadmin)",  # Common admin paths
    r"(?i)(?:\.env|\.git|\.github|\.gitignore|\.gitattributes|\.gitmodules|\.gitlab|\.gitlab-ci\.yml)",  # Version control and env files
    r"(?i)(?:\.DS_Store|\.idea|\.vscode|\.sublime|\.config|\.local|\.ssh|\.aws|\.npm|\.yarn)",  # IDE and config files
    r"(?i)(?:\.log|\.sql|\.bak|\.backup|\.old|\.swp|\.swo|\.tmp|\.temp|\.cache)",  # Backup and log files
    r"(?i)(?:\.htaccess|\.htpasswd|\.htgroup|\.htdigest|\.htdbm|\.htpass)",  # Apache config files
    r"(?i)(?:\.ini|\.conf|\.config|\.properties|\.xml|\.json|\.yaml|\.yml)",  # Config files
    r"(?i)(?:\.pem|\.key|\.crt|\.cer|\.der|\.p12|\.pfx|\.p7b|\.p7c|\.p7m|\.p7s)",  # Certificate and key files
    r"(?i)(?:\.db|\.sqlite|\.sqlite3|\.mdb|\.accdb|\.dbf|\.mdf|\.ldf|\.ndf)",  # Database files
    r"(?i)(?:\.php|\.asp|\.aspx|\.jsp|\.jspx|\.do|\.action|\.cgi|\.pl|\.py|\.rb|\.sh)",  # Script files
    r"(?i)(?:\.exe|\.dll|\.so|\.dylib|\.jar|\.war|\.ear|\.apk|\.ipa|\.app)",  # Executable files
    r"(?i)(?:\.zip|\.tar|\.gz|\.rar|\.7z|\.bz2|\.xz|\.tgz|\.tbz2|\.txz)",  # Archive files
    r"(?i)(?:\.pdf|\.doc|\.docx|\.xls|\.xlsx|\.ppt|\.pptx|\.odt|\.ods|\.odp)",  # Document files
    r"(?i)(?:\.jpg|\.jpeg|\.png|\.gif|\.bmp|\.tiff|\.webp|\.svg|\.ico)",  # Image files
    r"(?i)(?:\.mp3|\.mp4|\.avi|\.mov|\.wmv|\.flv|\.wav|\.ogg|\.m4a|\.m4v)",  # Media files
    r"(?i)(?:\.ttf|\.otf|\.woff|\.woff2|\.eot|\.sfnt|\.pfb|\.pfa|\.bdf|\.pcf)",  # Font files
    r"(?i)(?:\.css|\.scss|\.sass|\.less|\.styl|\.stylus|\.postcss)",  # Style files
    r"(?i)(?:\.js|\.jsx|\.ts|\.tsx|\.coffee|\.litcoffee|\.coffee\.md)",  # Script files
    r"(?i)(?:\.html|\.htm|\.xhtml|\.shtml|\.phtml|\.jhtml|\.dhtml)",  # HTML files
    r"(?i)(?:\.txt|\.text|\.md|\.markdown|\.rst|\.asciidoc|\.adoc|\.asc)",  # Text files
    r"(?i)(?:\.csv|\.tsv|\.tab|\.dat|\.data|\.raw|\.bin|\.hex)",  # Data files
    r"(?i)(?:\.lock|\.pid|\.sock|\.socket|\.fifo|\.pipe|\.sem|\.shm)",  # System files
    r"(?i)(?:\.bak|\.backup|\.old|\.new|\.tmp|\.temp|\.cache|\.swap)",  # Temporary files
]


class PenetrationDetector(BaseSecurityComponent):
    """
    Detect potential penetration attempts (synchronous).
    """

    # Default suspicious patterns
    DEFAULT_SUSPICIOUS_PATTERNS = SUSPICIOUS_PATTERNS

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

        # Use default patterns if none are specified
        suspicious_patterns = (
            self.config.suspicious_patterns or self.DEFAULT_SUSPICIOUS_PATTERNS
        )

        for pattern in suspicious_patterns:
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

    # Default suspicious patterns
    DEFAULT_SUSPICIOUS_PATTERNS = SUSPICIOUS_PATTERNS

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

        # Use default patterns if none are specified
        suspicious_patterns = (
            self.config.suspicious_patterns or self.DEFAULT_SUSPICIOUS_PATTERNS
        )

        for pattern in suspicious_patterns:
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
