from __future__ import annotations

import re


_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"sk-[A-Za-z0-9]{10,}"),
    re.compile(r"AKID[A-Za-z0-9]{10,}"),
    re.compile(r"AKI[A-Za-z0-9]{10,}"),
    re.compile(r"(?im)^(\\s*(DEEPSEEK_API_KEY|TENCENT_SECRET_ID|TENCENT_SECRET_KEY)\\s*=\\s*).+$"),
    re.compile(r"(?i)(api[_-]?key\\s*[=:]\\s*)(['\\\"]?)[A-Za-z0-9_\\-]{10,}\\2"),
    re.compile(r"(?i)(secret[_-]?key\\s*[=:]\\s*)(['\\\"]?)[A-Za-z0-9_\\-]{10,}\\2"),
]


def redact_secrets(text: str) -> str:
    out = text
    out = _PATTERNS[0].sub("sk-[REDACTED]", out)
    out = _PATTERNS[1].sub("AKID[REDACTED]", out)
    out = _PATTERNS[2].sub("AKI[REDACTED]", out)
    out = _PATTERNS[3].sub(r"\\1[REDACTED]", out)
    out = _PATTERNS[4].sub(r"\\1\\2[REDACTED]\\2", out)
    out = _PATTERNS[5].sub(r"\\1\\2[REDACTED]\\2", out)
    return out
