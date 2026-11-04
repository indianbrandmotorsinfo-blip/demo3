import json
import logging
from datetime import datetime, date
import portal.extensions as extensions

logger = logging.getLogger(__name__)


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)


class CacheService:
    """Enterprise Redis caching service with automated invalidation and safe fallback."""

    PREFIX = "portal:"
    DEFAULT_TTL = 300  # 5 minutes

    @classmethod
    def _key(cls, key: str) -> str:
        return f"{cls.PREFIX}{key}"

    @classmethod
    def get(cls, key: str):
        """Fetches and deserializes cached JSON object."""
        try:
            if not extensions.redis_client:
                return None
            val = extensions.redis_client.get(cls._key(key))
            if val:
                return json.loads(val)
        except Exception as exc:
            logger.warning(f"Cache GET error for key '{key}': {exc}")
        return None

    @classmethod
    def set(cls, key: str, value, ttl: int = None) -> bool:
        """Serializes and saves object to Redis cache."""
        try:
            if not extensions.redis_client:
                return False
            ttl = ttl or cls.DEFAULT_TTL
            serialized = json.dumps(value, cls=CustomJSONEncoder)
            return bool(extensions.redis_client.setex(cls._key(key), ttl, serialized))
        except Exception as exc:
            logger.warning(f"Cache SET error for key '{key}': {exc}")
            return False

    @classmethod
    def delete(cls, key: str) -> bool:
        """Deletes a single cache key."""
        try:
            if not extensions.redis_client:
                return False
            return bool(extensions.redis_client.delete(cls._key(key)))
        except Exception as exc:
            logger.warning(f"Cache DELETE error for key '{key}': {exc}")
            return False

    @classmethod
    def delete_pattern(cls, pattern: str) -> int:
        """Deletes all keys matching a pattern (uses SCAN, never blocks Redis)."""
        try:
            if not extensions.redis_client:
                return 0
            search = f"{cls.PREFIX}{pattern}"
            keys = list(extensions.redis_client.scan_iter(match=search, count=200))
            if keys:
                return extensions.redis_client.delete(*keys)
        except Exception as exc:
            logger.warning(f"Cache pattern invalidation error for '{pattern}': {exc}")
        return 0

    # Specific Cache Management Methods

    @classmethod
    def get_dashboard_stats(cls, role: str, user_id: int = None):
        key = f"dashboard:{role}:{user_id if user_id else 'global'}"
        return cls.get(key)

    @classmethod
    def set_dashboard_stats(cls, role: str, data, user_id: int = None, ttl: int = 180):
        key = f"dashboard:{role}:{user_id if user_id else 'global'}"
        return cls.set(key, data, ttl)

    @classmethod
    def get_assignment_detail(cls, assignment_id: int):
        return cls.get(f"assignment:{assignment_id}")

    @classmethod
    def set_assignment_detail(cls, assignment_id: int, data, ttl: int = 300):
        return cls.set(f"assignment:{assignment_id}", data, ttl)

    @classmethod
    def get_admin_statistics(cls):
        return cls.get("statistics:admin")

    @classmethod
    def set_admin_statistics(cls, data, ttl: int = 300):
        return cls.set("statistics:admin", data, ttl)

    # Invalidation Hooks

    @classmethod
    def invalidate_all_assignment_caches(cls, assignment_id: int = None):
        """Invalidates assignment details, assignment listings, dashboards, and statistics."""
        if assignment_id:
            cls.delete(f"assignment:{assignment_id}")
        cls.delete_pattern("assignments:*")
        cls.delete_pattern("dashboard:*")
        cls.delete_pattern("statistics:*")
        logger.info(f"Invalidated assignment and dashboard caches (assignment_id={assignment_id})")

    @classmethod
    def invalidate_submission_caches(cls):
        """Invalidates submission listings, statistics, and dashboards."""
        cls.delete_pattern("submissions:*")
        cls.delete_pattern("dashboard:*")
        cls.delete_pattern("statistics:*")
        logger.info("Invalidated submission and statistics caches")
