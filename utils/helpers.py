"""
utils/helpers.py
-----------------
Small, reusable utility functions used across services and routes.
"""

import uuid
from datetime import datetime


def generate_unique_filename(original_filename: str) -> str:
    """Create a collision-free filename while preserving the extension."""
    ext = original_filename.rsplit(".", 1)[1].lower() if "." in original_filename else "png"
    return f"{uuid.uuid4().hex}.{ext}"


def now_str() -> str:
    """Return the current timestamp formatted for display/storage."""
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


def get_client_ip(request) -> str:
    """
    Best-effort extraction of the client's IP address, respecting
    a reverse proxy's X-Forwarded-For header when present.
    """
    forwarded = request.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr or "unknown"


def classify_by_score(score: int, safe_max: int, suspicious_max: int) -> str:
    """Map a numeric risk score to a Safe / Suspicious / Dangerous label."""
    if score <= safe_max:
        return "Safe"
    if score <= suspicious_max:
        return "Suspicious"
    return "Dangerous"


def truncate(text: str, length: int = 80) -> str:
    """Truncate long strings for compact display in tables/UI."""
    if text is None:
        return ""
    return text if len(text) <= length else text[: length - 3] + "..."
