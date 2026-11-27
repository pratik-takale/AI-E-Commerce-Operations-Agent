import logging

import redis

from app.redis_client import get_redis

logger = logging.getLogger(__name__)


def product_key(product_id: int) -> str:
    return f"cache:product:{product_id}"


def get_value(key: str) -> str | None:
    """Read from cache. If Redis is down, behave as a cache miss."""
    try:
        return get_redis().get(key)
    except redis.RedisError:
        logger.warning("Redis unavailable, cache read skipped")
        return None


def set_value(key: str, value: str, ttl_seconds: int) -> None:
    try:
        get_redis().set(key, value, ex=ttl_seconds)
    except redis.RedisError:
        logger.warning("Redis unavailable, cache write skipped")


def invalidate_products(product_ids: list[int]) -> None:
    """Delete cached product data after price, details or stock changed."""
    if not product_ids:
        return
    try:
        get_redis().delete(*[product_key(pid) for pid in set(product_ids)])
    except redis.RedisError:
        logger.warning("Redis unavailable, cache invalidation skipped")