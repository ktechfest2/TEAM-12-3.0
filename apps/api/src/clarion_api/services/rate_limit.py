"""A small in-memory sliding window limiter. One per process, which is enough to blunt abuse
of the code endpoints; the per-number cooldown in the stored subscription is the strict rule."""

from collections import defaultdict, deque
from datetime import datetime, timedelta

from clarion_api.domain.errors import RateLimitedError


class SlidingWindowLimiter:
    def __init__(self, *, limit: int, window: timedelta) -> None:
        self._limit = limit
        self._window = window
        self._hits: dict[str, deque[datetime]] = defaultdict(deque)

    def hit(self, key: str, now: datetime) -> None:
        """Record a request or raise RateLimitedError when the key is over its limit."""
        hits = self._hits[key]
        while hits and now - hits[0] >= self._window:
            hits.popleft()
        if len(hits) >= self._limit:
            msg = "Too many requests. Please try again later."
            raise RateLimitedError(msg)
        hits.append(now)
