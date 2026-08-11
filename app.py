"""
app.py
------
Application entry point. Uses the Flask application-factory pattern
so the app can be created fresh for testing, the CLI, or WSGI servers.

Run locally with:
    python app.py
"""

import os
from flask import Flask, render_template

from config import config_map
from models.scan_model import db


def create_app(env: str = None) -> Flask:
    env = env or os.environ.get("FLASK_ENV", "development")
    app = Flask(__name__)
    app.config.from_object(config_map.get(env, config_map["default"]))

    # Ensure required directories exist
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["CSV_REPORT_FOLDER"], exist_ok=True)
    os.makedirs(app.config["PDF_REPORT_FOLDER"], exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(__file__), "database"), exist_ok=True)

    db.init_app(app)

    # --- Register blueprints ---
    from routes.main_routes import main_bp
    from routes.api_routes import api_bp
    from routes.admin_routes import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(admin_bp)

    # --- Error handlers ---
    @app.errorhandler(404)
    def not_found(e):
        return render_template("error.html", code=404, message="Page not found."), 404

    @app.errorhandler(413)
    def too_large(e):
        return render_template("error.html", code=413, message="Uploaded file is too large (max 8MB)."), 413

    @app.errorhandler(500)
    def server_error(e):
        return render_template("error.html", code=500, message="Something went wrong on our end."), 500

    # --- Create database tables on first run ---
    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"], host="0.0.0.0", port=5000)
