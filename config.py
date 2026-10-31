import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


TURSO_DATABASE_URL = os.environ.get("TURSO_DATABASE_URL")
TURSO_AUTH_TOKEN = os.environ.get("TURSO_AUTH_TOKEN")


def _database_uri():
    # On serverless platforms (e.g. Vercel) the local filesystem isn't
    # writable/persistent, so a Turso (hosted libSQL — SQLite-compatible)
    # database is used instead when credentials are present. Local
    # development and persistent-disk hosts (e.g. Render) keep using a
    # plain SQLite file.
    if TURSO_DATABASE_URL and TURSO_AUTH_TOKEN:
        # Accept either "host.turso.io" or "libsql://host.turso.io" (what
        # `turso db show --url` prints) — the dialect wants just the host.
        hostname = TURSO_DATABASE_URL.removeprefix("libsql://")
        return f"sqlite+libsql://{hostname}/?secure=true"

    return os.environ.get(
        "DATABASE_URL", "sqlite:///" + os.path.join(BASE_DIR, "instance", "app.db")
    )


def _engine_options():
    # The installed sqlalchemy-libsql dialect doesn't reliably pick an
    # "authToken" query-string parameter back out of the URL (connects
    # with an empty token), but libsql_experimental.connect() accepts
    # auth_token as a plain keyword — so pass it through connect_args
    # instead of the URL.
    if TURSO_DATABASE_URL and TURSO_AUTH_TOKEN:
        return {"connect_args": {"auth_token": TURSO_AUTH_TOKEN}}
    return {}


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
    SQLALCHEMY_DATABASE_URI = _database_uri()
    SQLALCHEMY_ENGINE_OPTIONS = _engine_options()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    WTF_CSRF_TIME_LIMIT = None
