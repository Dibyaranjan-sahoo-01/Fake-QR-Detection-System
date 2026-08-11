"""
services/url_analyzer.py
-------------------------
Parses and extracts structural features from a URL: scheme, host,
domain parts, subdomain count, and length -- the raw material the
phishing detector uses to reason about risk.
"""

from urllib.parse import urlparse
import tldextract

from utils.validators import is_valid_url, is_ip_address_host

# Use the bundled public-suffix-list snapshot instead of fetching it from
# publicsuffix.org on every cold start. This keeps the app fully functional
# offline / behind restrictive egress rules and avoids repeated network
# calls and 403s in sandboxed or air-gapped environments.
_TLD_EXTRACTOR = tldextract.TLDExtract(suffix_list_urls=(), cache_dir=None)


def analyze_url_structure(url: str) -> dict:
    """
    Break a URL down into structural components used by the
    phishing detector. Never raises -- returns is_valid=False
    on malformed input instead.
    """
    result = {
        "raw_url": url,
        "is_valid": False,
        "scheme": "",
        "host": "",
        "is_https": False,
        "domain": "",
        "subdomain": "",
        "suffix": "",
        "registered_domain": "",
        "subdomain_count": 0,
        "is_ip_host": False,
        "path": "",
        "query": "",
        "length": len(url) if url else 0,
    }

    if not url:
        return result

    result["is_valid"] = is_valid_url(url)

    try:
        parsed = urlparse(url)
        result["scheme"] = parsed.scheme.lower()
        result["is_https"] = result["scheme"] == "https"
        result["host"] = parsed.hostname or ""
        result["path"] = parsed.path or ""
        result["query"] = parsed.query or ""

        result["is_ip_host"] = is_ip_address_host(result["host"])

        extracted = _TLD_EXTRACTOR(url)
        result["domain"] = extracted.domain
        result["subdomain"] = extracted.subdomain
        result["suffix"] = extracted.suffix
        result["registered_domain"] = f"{extracted.domain}.{extracted.suffix}" if extracted.suffix else extracted.domain
        result["subdomain_count"] = len([s for s in extracted.subdomain.split(".") if s]) if extracted.subdomain else 0

    except Exception:
        # Malformed URL -- leave defaults, is_valid already reflects this
        pass

    return result
