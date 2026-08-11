"""
routes/main_routes.py
-----------------------
Page-rendering routes (HTML views). Actual scanning/analysis logic
lives in api_routes.py; these routes just serve templates and,
where useful, pre-fetch data for server-side rendering.
"""

from flask import Blueprint, render_template, request
from models.scan_model import ScanHistory
from services.report_generator import get_dashboard_stats

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """Landing page introducing the tool."""
    return render_template("index.html")


@main_bp.route("/scanner")
def scanner():
    """QR upload + live webcam scanner page."""
    return render_template("scanner.html")


@main_bp.route("/dashboard")
def dashboard():
    """Statistics dashboard."""
    stats = get_dashboard_stats()
    return render_template("dashboard.html", stats=stats)


@main_bp.route("/history")
def history():
    """Scan history with search/filter (filtering done client-side + API)."""
    page = request.args.get("page", 1, type=int)
    per_page = 20
    pagination = ScanHistory.query.order_by(ScanHistory.scan_datetime.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return render_template("history.html", scans=pagination.items, pagination=pagination)


@main_bp.route("/report")
def report():
    """Standalone printable report view."""
    stats = get_dashboard_stats()
    return render_template("report.html", stats=stats)


@main_bp.route("/result/<int:scan_id>")
def result(scan_id):
    """Shareable, standalone view of a single scan result."""
    scan = ScanHistory.query.get_or_404(scan_id)
    return render_template("result.html", scan=scan)
