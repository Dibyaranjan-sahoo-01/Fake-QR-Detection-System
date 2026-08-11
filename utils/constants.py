"""
utils/constants.py
-------------------
Static lookup data used by the phishing / risk-analysis engine.
Keeping these as data (not scattered magic strings) makes the
detection logic easy to extend and test.
"""

# Known URL-shortening domains. Shortened links hide the real
# destination, which is a common phishing technique.
SHORTENER_DOMAINS = {
    "bit.ly", "tinyurl.com", "goo.gl", "t.co", "ow.ly", "is.gd",
    "buff.ly", "adf.ly", "shorte.st", "cutt.ly", "rebrand.ly",
    "tiny.cc", "shorturl.at", "bl.ink", "rb.gy", "s.id", "v.gd",
}

# Keywords commonly seen in phishing / credential-harvesting URLs.
SUSPICIOUS_KEYWORDS = [
    "login", "verify", "password", "signin", "sign-in", "payment",
    "wallet", "bank", "free", "update", "gift", "secure", "account",
    "confirm", "billing", "suspend", "unlock", "reward", "bonus",
    "invoice", "security-alert", "verify-account", "recover",
]

# Suspicious top-level domains frequently abused for cheap,
# throwaway phishing infrastructure.
SUSPICIOUS_TLDS = {
    "xyz", "top", "click", "gq", "tk", "ml", "cf", "ga", "work",
    "support", "loan", "win", "review", "party", "date", "faith",
}

# Regex-friendly fragment used to detect raw IP addresses in a URL host.
IP_ADDRESS_PATTERN = r"^(\d{1,3}\.){3}\d{1,3}$"

# Threshold beyond which a URL is considered "very long" (often used
# to obfuscate the real destination or bury it after padding).
LONG_URL_LENGTH_THRESHOLD = 90

# Characters/patterns that indicate possible obfuscation (e.g. excessive
# hyphens, @ symbols used to trick the eye, punycode/xn-- prefixes).
OBFUSCATION_INDICATORS = ["@", "xn--", "%00", "%0d%0a", "\\u", "..", "0x"]

# Points added to the risk score for each detected issue.
# Total is clamped to 0-100 by the risk calculator.
RISK_WEIGHTS = {
    "no_https": 15,
    "shortened_url": 20,
    "ip_address_url": 25,
    "suspicious_keyword": 10,   # per keyword, capped
    "long_url": 10,
    "obfuscated_url": 20,
    "invalid_url_format": 15,
    "suspicious_tld": 15,
    "many_subdomains": 10,
    "safe_browsing_flagged": 40,
    "virustotal_flagged": 40,
}

# Classification labels
RESULT_SAFE = "Safe"
RESULT_SUSPICIOUS = "Suspicious"
RESULT_DANGEROUS = "Dangerous"

# QR content types
QR_TYPE_URL = "URL"
QR_TYPE_TEXT = "TEXT"
QR_TYPE_UNKNOWN = "UNKNOWN"
