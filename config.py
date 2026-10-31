import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def _database_uri():
    # On serverless platforms (e.g. Vercel) the local filesystem isn't
    # writable/persistent, so a Turso (hosted libSQL — SQLite-compatible)
    # database is used instead when credentials are present. Local
    # development and persistent-disk hosts (e.g. Render) keep using a
    # plain SQLite file.
    turso_url = os.environ.get("TURSO_DATABASE_URL")
    turso_token = os.environ.get("TURSO_AUTH_TOKEN")
    if turso_url and turso_token:
        # Accept either "host.turso.io" or "libsql://host.turso.io" (what
        # `turso db show --url` prints) — the dialect wants just the host.
        hostname = turso_url.removeprefix("libsql://")
        return f"sqlite+libsql://{hostname}?authToken={turso_token}&secure=true"

    return os.environ.get(
        "DATABASE_URL", "sqlite:///" + os.path.join(BASE_DIR, "instance", "app.db")
    )


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
    SQLALCHEMY_DATABASE_URI = _database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    WTF_CSRF_TIME_LIMIT = None
