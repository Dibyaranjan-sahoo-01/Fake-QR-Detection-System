"""
routes/api_routes.py
----------------------
RESTful JSON API: QR scanning (upload + webcam frame), scan history
retrieval with search/filter, single-record fetch, and CSV export.
"""

import os
import base64

from flask import Blueprint, request, jsonify, current_app, send_file

from models.scan_model import db, ScanHistory
from services.qr_scanner import decode_qr_from_image_path, decode_qr_from_bytes, QRDecodeError
from services.url_analyzer import analyze_url_structure
from services.phishing_detector import run_all_checks
from services.risk_calculator import evaluate
from services.export_csv import export_scans_to_csv
from utils.validators import allowed_file, sanitize_filename
from utils.helpers import generate_unique_filename, get_client_ip
from utils.constants import QR_TYPE_URL

api_bp = Blueprint("api", __name__, url_prefix="/api")


def _analyze_and_store(decoded: dict, source: str, user_ip: str, image_filename: str = None) -> ScanHistory:
    """Shared pipeline: analyze decoded QR content, score it, persist it."""
    content = decoded["content"]
    qr_type = decoded["type"]

    reasons = []
    if qr_type == QR_TYPE_URL:
        structure = analyze_url_structure(content)
        reasons = run_all_checks(
            content,
            structure,
            safe_browsing_key=current_app.config.get("GOOGLE_SAFE_BROWSING_API_KEY", ""),
            virustotal_key=current_app.config.get("VIRUSTOTAL_API_KEY", ""),
        )

    verdict = evaluate(
        reasons,
        safe_max=current_app.config["RISK_SAFE_MAX"],
        suspicious_max=current_app.config["RISK_SUSPICIOUS_MAX"],
    )

    record = ScanHistory(
        qr_type=qr_type,
        decoded_content=content,
        url=content if qr_type == QR_TYPE_URL else None,
        risk_score=verdict["risk_score"],
        scan_result=verdict["scan_result"],
        detection_reasons="; ".join(verdict["reasons"]) if verdict["reasons"] else "No issues detected",
        user_ip=user_ip,
        source=source,
        image_filename=image_filename,
    )
    db.session.add(record)
    db.session.commit()
    return record


@api_bp.route("/scan/upload", methods=["POST"])
def scan_upload():
    """Accept an uploaded image file, decode + analyze the QR code."""
    if "qr_image" not in request.files:
        return jsonify({"success": False, "error": "No file part named 'qr_image' in the request."}), 400

    file = request.files["qr_image"]
    if file.filename == "":
        return jsonify({"success": False, "error": "No file selected."}), 400

    if not allowed_file(file.filename, current_app.config["ALLOWED_EXTENSIONS"]):
        return jsonify({"success": False, "error": "Unsupported file type. Please upload a PNG, JPG, JPEG, BMP, GIF or WEBP image."}), 400

    safe_name = generate_unique_filename(sanitize_filename(file.filename))
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)
    filepath = os.path.join(upload_folder, safe_name)
    file.save(filepath)

    try:
        decoded = decode_qr_from_image_path(filepath)
    except QRDecodeError as e:
        return jsonify({"success": False, "error": str(e)}), 422
    except Exception:
        return jsonify({"success": False, "error": "An unexpected error occurred while processing the image."}), 500

    record = _analyze_and_store(
        decoded, source="upload", user_ip=get_client_ip(request), image_filename=safe_name
    )
    return jsonify({"success": True, "scan": record.to_dict()})


@api_bp.route("/scan/webcam", methods=["POST"])
def scan_webcam():
    """
    Accept a base64-encoded frame captured from the browser webcam,
    decode + analyze the QR code. Expects JSON: {"image": "data:image/png;base64,..."}
    """
    data = request.get_json(silent=True) or {}
    image_data = data.get("image", "")
    if not image_data:
        return jsonify({"success": False, "error": "No image data received."}), 400

    try:
        if "," in image_data:
            image_data = image_data.split(",", 1)[1]
        image_bytes = base64.b64decode(image_data)
    except Exception:
        return jsonify({"success": False, "error": "Invalid image data encoding."}), 400

    try:
        decoded = decode_qr_from_bytes(image_bytes)
    except QRDecodeError as e:
        return jsonify({"success": False, "error": str(e)}), 422
    except Exception:
        return jsonify({"success": False, "error": "An unexpected error occurred while processing the frame."}), 500

    record = _analyze_and_store(decoded, source="webcam", user_ip=get_client_ip(request))
    return jsonify({"success": True, "scan": record.to_dict()})


@api_bp.route("/history", methods=["GET"])
def get_history():
    """
    Return scan history as JSON, with optional search/filter query params:
    - q: substring match on decoded content / URL
    - result: Safe | Suspicious | Dangerous
    - qr_type: URL | TEXT
    """
    query = ScanHistory.query

    q = request.args.get("q", "").strip()
    if q:
        like = f"%{q}%"
        query = query.filter(
            db.or_(ScanHistory.decoded_content.ilike(like), ScanHistory.url.ilike(like))
        )

    result_filter = request.args.get("result", "").strip()
    if result_filter:
        query = query.filter(ScanHistory.scan_result == result_filter)

    type_filter = request.args.get("qr_type", "").strip()
    if type_filter:
        query = query.filter(ScanHistory.qr_type == type_filter)

    scans = query.order_by(ScanHistory.scan_datetime.desc()).limit(500).all()
    return jsonify({"success": True, "count": len(scans), "scans": [s.to_dict() for s in scans]})


@api_bp.route("/history/<int:scan_id>", methods=["GET"])
def get_scan(scan_id):
    """Fetch a single scan record by ID."""
    record = ScanHistory.query.get(scan_id)
    if not record:
        return jsonify({"success": False, "error": "Scan not found."}), 404
    return jsonify({"success": True, "scan": record.to_dict()})


@api_bp.route("/history/<int:scan_id>", methods=["DELETE"])
def delete_scan(scan_id):
    """Delete a single scan record (used by the admin panel)."""
    record = ScanHistory.query.get(scan_id)
    if not record:
        return jsonify({"success": False, "error": "Scan not found."}), 404
    db.session.delete(record)
    db.session.commit()
    return jsonify({"success": True, "message": f"Scan {scan_id} deleted."})


@api_bp.route("/export/csv", methods=["GET"])
def export_csv():
    """Export the full scan history as a downloadable CSV file."""
    scans = ScanHistory.query.order_by(ScanHistory.scan_datetime.desc()).all()
    filepath = export_scans_to_csv(scans, current_app.config["CSV_REPORT_FOLDER"])
    return send_file(filepath, as_attachment=True, download_name=os.path.basename(filepath))


@api_bp.route("/stats", methods=["GET"])
def stats():
    """Lightweight JSON stats endpoint (used to refresh dashboard widgets)."""
    from services.report_generator import get_dashboard_stats
    return jsonify({"success": True, "stats": get_dashboard_stats()})
