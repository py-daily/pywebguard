PENETRATION_DETECTION_SUSPICIOUS_PATTERNS = [
    # SQL Injection (common patterns)
    r"(?i)(union\s+select|select\s+.*\s+from|insert\s+into|update\s+.*\s+set|delete\s+from)",
    r"(?i)(or\s+1=1|--|#|/\*.*?\*/|;)",
    # XSS (most used vectors)
    r"(?i)(<script.*?>|javascript:|onerror=|onload=|document\.cookie|alert\s*\()",
    # Path Traversal (basic and encoded)
    r"(?i)(\.\./|\.\.\\|%2e%2e%2f|%2e%2e%5c)",
    # Command Injection
    r"(?i)(;|\|\||&&|\$\(.*?\)|`.*?`)",
    r"(?i)(cat\s+/etc/passwd|whoami|uname\s+-a|id)",
    # Sensitive file or config exposure
    r"(?i)(\.env|\.git|config\.yml|\.htaccess|\.log|\.sql|\.bak)",
    r"(?i)(<iframe|<img\s+src|<svg\s+onload)",  # More XSS tags
    r"(?i)(passwd|shadow|boot\.ini|win\.ini)",  # Sensitive system files
]
