PENETRATION_DETECTION_SUSPICIOUS_PATTERNS = [
    # SQL Injection patterns
    r"(?i)(?:union\s+select|select\s+.*\s+from|insert\s+into|update\s+.*\s+set|delete\s+from)",
    r"(?i)(?:drop\s+table|alter\s+table|truncate\s+table|exec\s+xp_cmdshell)",
    r"(?i)(?:--\s*$|/\*.*?\*/|;.*?$)",  # SQL comments
    r'(?i)(?:\'|"|`)\s*(?:or|and)\s*(?:\d+|\w+)\s*=\s*(?:\d+|\w+)',  # SQL boolean injection
    r"(?i)(?:waitfor\s+delay|benchmark\s*\(|sleep\s*\(|pg_sleep\s*\()",  # SQL timing attacks
    # XSS patterns
    r"(?i)(?:<script>|javascript:|onerror=|onload=|eval\(|setTimeout\(|document\.cookie)",
    r"(?i)(?:on\w+\s*=|data:\s*text\/html|vbscript:|expression\s*\()",  # More XSS vectors
    r"(?i)(?:alert\s*\(|confirm\s*\(|prompt\s*\()",  # Common XSS functions
    r'(?i)(?:<img\s+src\s*=\s*[\'"]?\s*x\s*:\s*onerror\s*=\s*[\'"]?\s*alert\s*\()',  # Image XSS
    r'(?i)(?:<svg\s+onload\s*=\s*[\'"]?\s*alert\s*\()',  # SVG XSS
    # Path Traversal patterns
    r"(?i)(?:\.\.\/|\.\.\\|\/etc\/passwd|\/bin\/bash|cmd\.exe|command\.com)",
    r"(?i)(?:\.\.%2f|\.\.%5c|%2e%2e%2f|%2e%2e%5c)",  # URL encoded path traversal
    r"(?i)(?:\.\.\/\.\.\/\.\.\/|\.\.\\\.\.\\\.\.\\)",  # Multiple levels
    r"(?i)(?:\.\.\/\.\.\/\.\.\/\.\.\/|\.\.\\\.\.\\\.\.\\\.\.\\)",  # More levels
    # Command Injection patterns
    r"(?i)(?:;|\|\||&&|\$\(|`|\\|\|)",  # Command separators
    r"(?i)(?:ls|cat|pwd|whoami|id|uname|net\s+user|net\s+group|ipconfig|ifconfig)",
    r"(?i)(?:rm\s+-rf|del\s+/[fqs]|erase\s+/[fqs])",  # Dangerous commands
    r"(?i)(?:wget|curl|nc|telnet|ftp|tftp|ssh|scp|sftp)",  # Network tools
    r"(?i)(?:chmod|chown|chgrp|chattr|setfacl)",  # Permission modification
    # Common admin paths
    r"(?i)(?:\/wp-admin|\/wp-login|\/administrator|\/admin|\/phpmyadmin)",
    # Version control and env files
    r"(?i)(?:\.env|\.git|\.github|\.gitignore|\.gitattributes|\.gitmodules|\.gitlab|\.gitlab-ci\.yml)",
    # IDE and config files
    r"(?i)(?:\.DS_Store|\.idea|\.vscode|\.sublime|\.config|\.local|\.ssh|\.aws|\.npm|\.yarn)",
    # Backup and log files
    r"(?i)(?:\.log|\.sql|\.bak|\.backup|\.old|\.swp|\.swo|\.tmp|\.temp|\.cache)",
    # Apache config files
    r"(?i)(?:\.htaccess|\.htpasswd|\.htgroup|\.htdigest|\.htdbm|\.htpass)",
    # Config files
    r"(?i)(?:\.ini|\.conf|\.config|\.properties|\.xml|\.json|\.yaml|\.yml)",
    # Certificate and key files
    r"(?i)(?:\.pem|\.key|\.crt|\.cer|\.der|\.p12|\.pfx|\.p7b|\.p7c|\.p7m|\.p7s)",
    # Database files
    r"(?i)(?:\.db|\.sqlite|\.sqlite3|\.mdb|\.accdb|\.dbf|\.mdf|\.ldf|\.ndf)",
    # Script files
    r"(?i)(?:\.php|\.asp|\.aspx|\.jsp|\.jspx|\.do|\.action|\.cgi|\.pl|\.py|\.rb|\.sh)",
    # Executable files
    r"(?i)(?:\.exe|\.dll|\.so|\.dylib|\.jar|\.war|\.ear|\.apk|\.ipa|\.app)",
    # Archive files
    r"(?i)(?:\.zip|\.tar|\.gz|\.rar|\.7z|\.bz2|\.xz|\.tgz|\.tbz2|\.txz)",
    # Document files
    r"(?i)(?:\.pdf|\.doc|\.docx|\.xls|\.xlsx|\.ppt|\.pptx|\.odt|\.ods|\.odp)",
    # Image files
    r"(?i)(?:\.jpg|\.jpeg|\.png|\.gif|\.bmp|\.tiff|\.webp|\.svg|\.ico)",
    # Media files
    r"(?i)(?:\.mp3|\.mp4|\.avi|\.mov|\.wmv|\.flv|\.wav|\.ogg|\.m4a|\.m4v)",
    # Font files
    r"(?i)(?:\.ttf|\.otf|\.woff|\.woff2|\.eot|\.sfnt|\.pfb|\.pfa|\.bdf|\.pcf)",
    # Style files
    r"(?i)(?:\.css|\.scss|\.sass|\.less|\.styl|\.stylus|\.postcss)",
    # Script files
    r"(?i)(?:\.js|\.jsx|\.ts|\.tsx|\.coffee|\.litcoffee|\.coffee\.md)",
    # HTML files
    r"(?i)(?:\.html|\.htm|\.xhtml|\.shtml|\.phtml|\.jhtml|\.dhtml)",
    # Text files
    r"(?i)(?:\.txt|\.text|\.md|\.markdown|\.rst|\.asciidoc|\.adoc|\.asc)",
    # Data files
    r"(?i)(?:\.csv|\.tsv|\.tab|\.dat|\.data|\.raw|\.bin|\.hex)",
    # System files
    r"(?i)(?:\.lock|\.pid|\.sock|\.socket|\.fifo|\.pipe|\.sem|\.shm)",
    # Temporary files
    r"(?i)(?:\.bak|\.backup|\.old|\.new|\.tmp|\.temp|\.cache|\.swap)",
]
