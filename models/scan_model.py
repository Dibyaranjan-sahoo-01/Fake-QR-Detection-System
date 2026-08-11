"""
models/scan_model.py
---------------------
SQLAlchemy ORM model representing a single QR-code scan record.
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class ScanHistory(db.Model):
    """Stores every scanned QR code and its analysis result."""

    __tablename__ = "scan_history"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    scan_datetime = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    qr_type = db.Column(db.String(20), nullable=False, default="UNKNOWN")
    decoded_content = db.Column(db.Text, nullable=False)
    url = db.Column(db.String(2048), nullable=True)
    risk_score = db.Column(db.Integer, nullable=False, default=0)
    scan_result = db.Column(db.String(20), nullable=False, default="Safe")
    detection_reasons = db.Column(db.Text, nullable=True)  # stored as "; " joined string
    user_ip = db.Column(db.String(64), nullable=True)
    source = db.Column(db.String(20), nullable=False, default="upload")  # upload | webcam
    image_filename = db.Column(db.String(255), nullable=True)

    def to_dict(self):
        """Serialize the record for JSON API responses."""
        return {
            "id": self.id,
            "scan_datetime": self.scan_datetime.strftime("%Y-%m-%d %H:%M:%S") if self.scan_datetime else None,
            "qr_type": self.qr_type,
            "decoded_content": self.decoded_content,
            "url": self.url,
            "risk_score": self.risk_score,
            "scan_result": self.scan_result,
            "detection_reasons": self.detection_reasons.split("; ") if self.detection_reasons else [],
            "user_ip": self.user_ip,
            "source": self.source,
            "image_filename": self.image_filename,
        }

    def __repr__(self):
        return f"<ScanHistory id={self.id} result={self.scan_result} score={self.risk_score}>"
