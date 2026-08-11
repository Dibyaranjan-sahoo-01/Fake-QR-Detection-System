"""
utils/validators.py
--------------------
Input validation helpers: uploaded-file safety checks and
URL syntax validation. Keeping validation centralized avoids
duplicated (and inconsistently correct) checks across routes.
"""

import os
import re
import validators as validators_lib

from utils.constants import IP_ADDRESS_PATTERN


def allowed_file(filename: str, allowed_extensions: set) -> bool:
    """Return True if the filename has an allowed image extension."""
    if not filename or "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in allowed_extensions


def is_valid_url(url: str) -> bool:
    """Strict URL syntax validation using the `validators` library."""
    if not url or not isinstance(url, str):
        return False
    try:
        return bool(validators_lib.url(url))
    except Exception:
        return False


def is_ip_address_host(host: str) -> bool:
    """Return True if the given hostname is a raw IPv4 address."""
    if not host:
        return False
    return bool(re.match(IP_ADDRESS_PATTERN, host))


def sanitize_filename(filename: str) -> str:
    """Strip directory components and unsafe characters from a filename."""
    filename = os.path.basename(filename)
    filename = re.sub(r"[^A-Za-z0-9_.\-]", "_", filename)
    return filename


def is_safe_upload_path(base_folder: str, filepath: str) -> bool:
    """
    Guard against path traversal: ensure the resolved file path is
    actually inside the intended upload folder.
    """
    base = os.path.abspath(base_folder)
    target = os.path.abspath(filepath)
    return target.startswith(base)
