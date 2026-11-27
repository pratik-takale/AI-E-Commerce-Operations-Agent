import redis

from app.config import settings

# One shared client. It manages its own connection pool and is thread-safe.
_client = redis.Redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,       # return str instead of bytes
    socket_connect_timeout=2,
    socket_timeout=2,
)


def get_redis() -> redis.Redis:
    return _client