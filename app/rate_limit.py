import time
from collections import defaultdict, deque
from threading import Lock
from typing import Any, cast

from redis import Redis
from redis.exceptions import RedisError

from app.config import Settings


class LoginRateLimiter:
    def __init__(self, config: Settings) -> None:
        self.limit = config.login_rate_limit
        self.window = config.login_rate_window_seconds
        self._attempts: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()
        self._redis = (
            Redis.from_url(
                config.redis_url,
                decode_responses=True,
                socket_connect_timeout=0.2,
                socket_timeout=0.2,
            )
            if config.redis_url
            else None
        )

    def check(self, client_ip: str) -> bool:
        if self._redis is not None:
            try:
                key = f"login-rate:{client_ip}"
                count = int(cast(Any, self._redis.incr(key)))
                if count == 1:
                    self._redis.expire(key, self.window)
                return count <= self.limit
            except RedisError:
                pass
        return self._check_memory(client_ip)

    def reset(self, client_ip: str) -> None:
        if self._redis is not None:
            try:
                self._redis.delete(f"login-rate:{client_ip}")
            except RedisError:
                pass
        with self._lock:
            self._attempts.pop(client_ip, None)

    def _check_memory(self, client_ip: str) -> bool:
        now = time.monotonic()
        with self._lock:
            attempts = self._attempts[client_ip]
            while attempts and attempts[0] <= now - self.window:
                attempts.popleft()
            if len(attempts) >= self.limit:
                return False
            attempts.append(now)
            return True
