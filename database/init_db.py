"""
database/init_db.py
--------------------
Standalone script to (re)initialize the SQLite database.
Run with:  python database/init_db.py
"""

import os
import sys

# Allow running this script directly from the project root or from /database
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from models.scan_model import db


def init_database():
    app = create_app()
    with app.app_context():
        db.create_all()
        print("Database initialized successfully at:", app.config["SQLALCHEMY_DATABASE_URI"])


if __name__ == "__main__":
    init_database()
