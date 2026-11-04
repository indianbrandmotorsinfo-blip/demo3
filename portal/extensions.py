import logging

import redis
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

logger = logging.getLogger(__name__)

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()

login_manager.login_view = "auth.login"
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "warning"

# Shared Redis client, or None when caching is disabled / unavailable.
#
# NOTE: the old in-memory "MockRedisClient" fallback was removed on purpose. On a
# serverless platform every instance has its own memory, so a per-process fake cache
# can never be invalidated across instances and would serve stale dashboards.
# With no Redis the app simply reads from Postgres every time.
redis_client = None


def init_redis(app):
    """Connect to Redis if REDIS_URL is configured; otherwise run uncached."""
    global redis_client
    redis_client = None

    redis_url = app.config.get("REDIS_URL")
    if not redis_url:
        logger.info("REDIS_URL not set - caching disabled.")
        return

    try:
        client = redis.from_url(
            redis_url,
            decode_responses=True,
            socket_timeout=1.5,
            socket_connect_timeout=1.5,
        )
        client.ping()
        redis_client = client
        logger.info("Connected to Redis - caching enabled.")
    except Exception as exc:
        logger.warning("Redis unavailable (%s) - continuing without cache.", exc)
        redis_client = None
