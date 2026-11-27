import logging

import redis
from fastapi import HTTPException

from app.redis_client import get_redis

logger = logging.getLogger(__name__)


def enforce_rate_limit(scope: str, identifier: str, limit: int, window_seconds: int = 60) -> None:
    """Fixed-window counter. Raises 429 when the identifier exceeds the limit."""
    key = f"ratelimit:{scope}:{identifier}"
    try:
        client = get_redis()
        pipe = client.pipeline()
        pipe.incr(key)
        pipe.ttl(key)
        count, ttl = pipe.execute()
        if ttl == -1:  # key exists without expiry (first hit): start the window
            client.expire(key, window_seconds)
            ttl = window_seconds
    except redis.RedisError:
        # Fail open: if Redis is down, do not block users
        logger.warning("Redis unavailable, rate limiting skipped")
        return

    if count > limit:
        raise HTTPException(
            status_code=429,
            detail={"code": "RATE_LIMITED", "message": "Too many requests. Please try again later."},
            headers={"Retry-After": str(max(ttl, 1))},
        )