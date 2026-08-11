"""
routes/admin_routes.py
------------------------
Minimal session-based admin panel for managing scan history.
Not intended as a full auth system -- swap in Flask-Login /
proper hashing + a real user table before any production use.
"""

from functools import wraps

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app

from models.scan_model import db, ScanHistory

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("admin.login"))
        return view(*args, **kwargs)
    return wrapped


@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if username == current_app.config["ADMIN_USERNAME"] and password == current_app.config["ADMIN_PASSWORD"]:
            session["is_admin"] = True
            return redirect(url_for("admin.panel"))
        flash("Invalid username or password.", "error")
    return render_template("admin.html", logged_in=False)


@admin_bp.route("/logout")
def logout():
    session.pop("is_admin", None)
    return redirect(url_for("admin.login"))


@admin_bp.route("/", methods=["GET"])
@login_required
def panel():
    scans = ScanHistory.query.order_by(ScanHistory.scan_datetime.desc()).all()
    return render_template("admin.html", logged_in=True, scans=scans)


@admin_bp.route("/delete/<int:scan_id>", methods=["POST"])
@login_required
def delete_scan(scan_id):
    record = ScanHistory.query.get(scan_id)
    if record:
        db.session.delete(record)
        db.session.commit()
        flash(f"Scan #{scan_id} deleted.", "success")
    return redirect(url_for("admin.panel"))


@admin_bp.route("/clear-all", methods=["POST"])
@login_required
def clear_all():
    db.session.query(ScanHistory).delete()
    db.session.commit()
    flash("All scan history cleared.", "success")
    return redirect(url_for("admin.panel"))
