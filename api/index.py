"""Vercel serverless entrypoint. Vercel's Python runtime looks for a WSGI
callable named `app` in this file."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import app  # noqa: E402
from models import User, db  # noqa: E402
from seed import populate  # noqa: E402

with app.app_context():
    db.create_all()
    if User.query.count() == 0:
        populate()
