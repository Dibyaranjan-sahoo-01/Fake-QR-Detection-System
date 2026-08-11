"""
services/phishing_detector.py
------------------------------
Applies heuristic phishing/malicious-URL checks to a parsed URL
and (optionally) external threat-intel APIs. Returns a list of
triggered "reasons", each mapped to a risk weight by the caller.
"""

import requests

from utils.constants import (
    SHORTENER_DOMAINS,
    SUSPICIOUS_KEYWORDS,
    SUSPICIOUS_TLDS,
    LONG_URL_LENGTH_THRESHOLD,
    OBFUSCATION_INDICATORS,
)


def check_https(structure: dict, reasons: list):
    if structure["is_valid"] and not structure["is_https"]:
        reasons.append(("no_https", "URL does not use HTTPS (insecure HTTP)"))


def check_shortener(structure: dict, reasons: list):
    registered = structure.get("registered_domain", "").lower()
    if registered in SHORTENER_DOMAINS:
        reasons.append(("shortened_url", f"URL uses a link shortener ({registered}) which can hide the real destination"))


def check_ip_host(structure: dict, reasons: list):
    if structure.get("is_ip_host"):
        reasons.append(("ip_address_url", "URL uses a raw IP address instead of a domain name"))


def check_suspicious_keywords(url: str, reasons: list):
    lowered = url.lower()
    hits = [kw for kw in SUSPICIOUS_KEYWORDS if kw in lowered]
    if hits:
        shown = ", ".join(hits[:5])
        reasons.append(("suspicious_keyword", f"Contains suspicious keyword(s): {shown}", len(hits)))


def check_long_url(structure: dict, reasons: list):
    if structure.get("length", 0) > LONG_URL_LENGTH_THRESHOLD:
        reasons.append(("long_url", f"URL is unusually long ({structure['length']} characters)"))


def check_obfuscation(url: str, reasons: list):
    lowered = url.lower()
    hits = [ind for ind in OBFUSCATION_INDICATORS if ind in lowered]
    if hits:
        reasons.append(("obfuscated_url", f"URL contains obfuscation indicators: {', '.join(hits)}"))


def check_valid_format(structure: dict, reasons: list):
    if not structure.get("is_valid"):
        reasons.append(("invalid_url_format", "URL does not match standard URL format"))


def check_suspicious_tld(structure: dict, reasons: list):
    suffix = structure.get("suffix", "").lower()
    if suffix in SUSPICIOUS_TLDS:
        reasons.append(("suspicious_tld", f"URL uses a top-level domain often abused for phishing (.{suffix})"))


def check_many_subdomains(structure: dict, reasons: list):
    if structure.get("subdomain_count", 0) >= 3:
        reasons.append(("many_subdomains", f"URL has an unusually high number of subdomains ({structure['subdomain_count']})"))


def check_google_safe_browsing(url: str, api_key: str, reasons: list):
    """Optional: query Google Safe Browsing API v4 if a key is configured."""
    if not api_key:
        return
    try:
        endpoint = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={api_key}"
        payload = {
            "client": {"clientId": "fake-qr-detector", "clientVersion": "1.0"},
            "threatInfo": {
                "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"],
                "platformTypes": ["ANY_PLATFORM"],
                "threatEntryTypes": ["URL"],
                "threatEntries": [{"url": url}],
            },
        }
        resp = requests.post(endpoint, json=payload, timeout=5)
        if resp.ok and resp.json().get("matches"):
            reasons.append(("safe_browsing_flagged", "Flagged by Google Safe Browsing as a known threat"))
    except requests.RequestException:
        # Fail gracefully -- external API issues should never break a scan
        pass


def check_virustotal(url: str, api_key: str, reasons: list):
    """Optional: query VirusTotal API v3 if a key is configured."""
    if not api_key:
        return
    try:
        import base64
        url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
        endpoint = f"https://www.virustotal.com/api/v3/urls/{url_id}"
        headers = {"x-apikey": api_key}
        resp = requests.get(endpoint, headers=headers, timeout=5)
        if resp.ok:
            stats = resp.json().get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
            if stats.get("malicious", 0) > 0 or stats.get("suspicious", 0) > 0:
                reasons.append(("virustotal_flagged", "Flagged by VirusTotal as malicious/suspicious"))
    except requests.RequestException:
        pass


def run_all_checks(url: str, structure: dict, safe_browsing_key: str = "", virustotal_key: str = "") -> list:
    """
    Run every heuristic (and any configured external) check against
    the URL. Returns a list of reason tuples:
        (weight_key, human_readable_message[, multiplier])
    """
    reasons = []

    check_valid_format(structure, reasons)
    check_https(structure, reasons)
    check_shortener(structure, reasons)
    check_ip_host(structure, reasons)
    check_suspicious_keywords(url, reasons)
    check_long_url(structure, reasons)
    check_obfuscation(url, reasons)
    check_suspicious_tld(structure, reasons)
    check_many_subdomains(structure, reasons)

    # Optional external intelligence (no-ops if keys are blank)
    check_google_safe_browsing(url, safe_browsing_key, reasons)
    check_virustotal(url, virustotal_key, reasons)

    return reasons
