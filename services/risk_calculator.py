"""
services/risk_calculator.py
-----------------------------
Converts a list of detection "reasons" (from phishing_detector) into
a single 0-100 risk score and a Safe / Suspicious / Dangerous label.
"""

from utils.constants import (
    RISK_WEIGHTS,
    RESULT_SAFE,
    RESULT_SUSPICIOUS,
    RESULT_DANGEROUS,
)


def calculate_risk_score(reasons: list) -> tuple:
    """
    reasons: list of tuples produced by phishing_detector.run_all_checks
             e.g. ("no_https", "message") or ("suspicious_keyword", "message", count)

    Returns: (score: int, reason_messages: list[str])
    """
    score = 0
    messages = []

    for reason in reasons:
        key = reason[0]
        message = reason[1]
        multiplier = reason[2] if len(reason) > 2 else 1

        weight = RISK_WEIGHTS.get(key, 5)
        if key == "suspicious_keyword":
            # Cap keyword contribution so 10 hits don't blow the scale
            score += min(weight * multiplier, 30)
        else:
            score += weight

        messages.append(message)

    score = max(0, min(100, score))
    return score, messages


def classify_result(score: int, safe_max: int, suspicious_max: int) -> str:
    """Map the numeric score to a human-readable classification."""
    if score <= safe_max:
        return RESULT_SAFE
    if score <= suspicious_max:
        return RESULT_SUSPICIOUS
    return RESULT_DANGEROUS


def evaluate(reasons: list, safe_max: int = 30, suspicious_max: int = 65) -> dict:
    """Convenience wrapper returning score, label, and reasons together."""
    score, messages = calculate_risk_score(reasons)
    label = classify_result(score, safe_max, suspicious_max)
    return {
        "risk_score": score,
        "scan_result": label,
        "reasons": messages,
    }
