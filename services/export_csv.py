"""
services/export_csv.py
------------------------
Exports scan history records to a CSV report file.
"""

import csv
import os
from datetime import datetime


CSV_HEADERS = [
    "Scan ID", "Scan Date & Time", "QR Type", "Decoded Content",
    "URL", "Risk Score", "Scan Result", "Detection Reasons", "User IP", "Source",
]


def export_scans_to_csv(scans: list, output_folder: str) -> str:
    """
    Write the given list of ScanHistory objects (or dicts) to a
    timestamped CSV file inside output_folder. Returns the file path.
    """
    os.makedirs(output_folder, exist_ok=True)
    filename = f"scan_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    filepath = os.path.join(output_folder, filename)

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(CSV_HEADERS)

        for scan in scans:
            data = scan.to_dict() if hasattr(scan, "to_dict") else scan
            writer.writerow([
                data.get("id"),
                data.get("scan_datetime"),
                data.get("qr_type"),
                data.get("decoded_content"),
                data.get("url"),
                data.get("risk_score"),
                data.get("scan_result"),
                "; ".join(data.get("detection_reasons", []) or []),
                data.get("user_ip"),
                data.get("source"),
            ])

    return filepath
