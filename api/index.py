"""Vercel serverless entrypoint. Vercel's Python runtime looks for a WSGI
callable named `app` in this file.

Note: this only creates the schema, it does NOT auto-seed demo data. The
Turso-backed deployment is seeded once, out of band, with:
    python -c "from seed import seed; seed()"
Seeding is hundreds of individual network round-trips to the remote
database, which is far too slow to run inside a single serverless function
invocation (and would just reproduce the 500 we're avoiding)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import app  # noqa: E402
from models import db  # noqa: E402

with app.app_context():
    db.create_all()
