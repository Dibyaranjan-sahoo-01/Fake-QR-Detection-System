"""
services/report_generator.py
------------------------------
Aggregates scan history into dashboard-ready statistics
(counts by classification, recent activity, risk distribution).
"""

from sqlalchemy import func

from models.scan_model import db, ScanHistory
from utils.constants import RESULT_SAFE, RESULT_SUSPICIOUS, RESULT_DANGEROUS


def get_dashboard_stats() -> dict:
    """Compute the summary numbers shown on the dashboard."""
    total_scans = db.session.query(func.count(ScanHistory.id)).scalar() or 0

    def count_by_result(result_label):
        return db.session.query(func.count(ScanHistory.id)).filter(
            ScanHistory.scan_result == result_label
        ).scalar() or 0

    safe_count = count_by_result(RESULT_SAFE)
    suspicious_count = count_by_result(RESULT_SUSPICIOUS)
    dangerous_count = count_by_result(RESULT_DANGEROUS)

    recent = (
        ScanHistory.query.order_by(ScanHistory.scan_datetime.desc()).limit(10).all()
    )

    # Simple bucketed risk distribution for charting (0-20, 21-40, ... 81-100)
    buckets = {"0-20": 0, "21-40": 0, "41-60": 0, "61-80": 0, "81-100": 0}
    all_scores = db.session.query(ScanHistory.risk_score).all()
    for (score,) in all_scores:
        if score <= 20:
            buckets["0-20"] += 1
        elif score <= 40:
            buckets["21-40"] += 1
        elif score <= 60:
            buckets["41-60"] += 1
        elif score <= 80:
            buckets["61-80"] += 1
        else:
            buckets["81-100"] += 1

    return {
        "total_scans": total_scans,
        "safe_count": safe_count,
        "suspicious_count": suspicious_count,
        "dangerous_count": dangerous_count,
        "recent_activity": [r.to_dict() for r in recent],
        "risk_distribution": buckets,
    }
