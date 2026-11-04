import os
from datetime import timedelta
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

from dotenv import load_dotenv

load_dotenv()
load_dotenv(".env.local")  # written by `vercel env pull`

ON_VERCEL = bool(os.getenv("VERCEL"))


def _env_bool(name: str, default: bool = False) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "on")


def _normalise_db_url(url: str) -> str:
    """Make a Postgres URL safe for SQLAlchemy + psycopg2.

    * ``postgres://``  -> ``postgresql://`` (Heroku/Vercel style prefix)
    * drops the ``supa=...`` query param that the Vercel<->Supabase integration
      appends; psycopg2 rejects unknown libpq options.
    * adds ``sslmode=require`` for remote hosts when not specified.
    """
    if not url:
        return url
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)

    parts = urlsplit(url)
    query = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True) if k != "supa"]
    host = parts.hostname or ""
    if (
        parts.scheme.startswith("postgresql")
        and host not in ("localhost", "127.0.0.1", "")
        and not any(k == "sslmode" for k, _ in query)
    ):
        query.append(("sslmode", "require"))
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


def _database_url() -> str:
    # DATABASE_URL is preferred; POSTGRES_URL is what Vercel's Supabase/Neon integrations inject.
    raw = (
        os.getenv("DATABASE_URL")
        or os.getenv("POSTGRES_URL")
        or "postgresql://postgres:postgres@localhost:5432/assignment_portal_db"
    )
    return _normalise_db_url(raw)


class BaseConfig:
    """Shared defaults."""

    SECRET_KEY = os.getenv("SECRET_KEY", "assignment-portal-insecure-dev-secret-key-999")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = _database_url()

    # Serverless: every instance keeps a *small* pool; stale connections are
    # detected before use and recycled quickly (Supabase pooler drops idle ones).
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_size": int(os.getenv("DB_POOL_SIZE", "2")),
        "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "3")),
        "pool_recycle": int(os.getenv("DB_POOL_RECYCLE", "240")),
    }

    # Optional cache. Leave REDIS_URL unset to run without caching.
    # (Vercel's Upstash/Redis integrations inject REDIS_URL or KV_URL.)
    REDIS_URL = os.getenv("REDIS_URL") or os.getenv("KV_URL") or ""
    REDIS_DEFAULT_TIMEOUT = int(os.getenv("REDIS_DEFAULT_TIMEOUT", "300"))

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = timedelta(
        seconds=int(os.getenv("PERMANENT_SESSION_LIFETIME", "86400"))
    )

    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600

    # Password-reset links are shown on-page because no email provider is wired up.
    # That is only acceptable for local demos, so it is OFF in production by default.
    SHOW_RESET_LINK = False
    PASSWORD_RESET_MAX_AGE = 3600  # seconds

    # Token protecting POST /internal/init-db (disabled when empty).
    INIT_TOKEN = os.getenv("INIT_TOKEN", "")

    APP_NAME = "Assignment Group Portal"
    ITEMS_PER_PAGE = 10
    ALLOWED_GROUP_SIZES = [1, 2, 3, 4, 5]


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SESSION_COOKIE_SECURE = False
    SQLALCHEMY_ECHO = False
    SHOW_RESET_LINK = True


class TestingConfig(BaseConfig):
    TESTING = True
    DEBUG = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URL", "sqlite:///:memory:")
    SQLALCHEMY_ENGINE_OPTIONS = {}  # pool options are not valid for in-memory SQLite
    REDIS_URL = ""  # caching disabled in tests
    SHOW_RESET_LINK = True


class ProductionConfig(BaseConfig):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    WTF_CSRF_SSL_STRICT = True
    SHOW_RESET_LINK = _env_bool("SHOW_RESET_LINK", False)

    @classmethod
    def validate(cls):
        if not os.getenv("SECRET_KEY"):
            raise RuntimeError(
                "SECRET_KEY is not set. Add it in Vercel -> Project -> Settings -> Environment Variables "
                "(generate one with: python -c \"import secrets; print(secrets.token_hex(32))\")."
            )
        if not (os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL")):
            raise RuntimeError("DATABASE_URL is not set. Point it at your Supabase/Neon Postgres database.")


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}


def default_config_name() -> str:
    """FLASK_ENV wins; otherwise any Vercel deployment is 'production'."""
    explicit = os.getenv("FLASK_ENV")
    if explicit:
        return explicit.lower()
    return "production" if ON_VERCEL else "development"
