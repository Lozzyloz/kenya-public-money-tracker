import threading
import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request

from app.core.config import settings

_limiters: list["SlidingWindowLimiter"] = []


class SlidingWindowLimiter:
    """In-memory limiter: per process, resets on restart. Fine for one server."""

    def __init__(self, limit: int, window_seconds: int):
        self.limit = limit
        self.window = window_seconds
        self.hits: dict[str, deque[float]] = defaultdict(deque)
        self.lock = threading.Lock()
        _limiters.append(self)

    def check(self, key: str) -> None:
        now = time.monotonic()
        with self.lock:
            if len(self.hits) > 10_000:  # drop stale keys so memory stays bounded
                for stale in [k for k, q in self.hits.items() if not q or now - q[-1] > self.window]:
                    del self.hits[stale]
            queue = self.hits[key]
            while queue and now - queue[0] > self.window:
                queue.popleft()
            if len(queue) >= self.limit:
                retry = int(self.window - (now - queue[0])) + 1
                raise HTTPException(
                    status_code=429,
                    detail="Too many requests. Please try again later.",
                    headers={"Retry-After": str(retry)},
                )
            queue.append(now)

    def reset(self) -> None:
        with self.lock:
            self.hits.clear()


def reset_all() -> None:
    for limiter in _limiters:
        limiter.reset()


def client_ip(request: Request) -> str:
    if settings.trust_proxy_headers:
        forwarded = request.headers.get("cf-connecting-ip") or request.headers.get(
            "x-forwarded-for", ""
        ).split(",")[0].strip()
        if forwarded:
            return forwarded
    return request.client.host if request.client else "unknown"


report_limiter = SlidingWindowLimiter(
    settings.report_rate_limit, settings.report_rate_window_seconds
)


def limit_report_submissions(request: Request) -> None:
    report_limiter.check(client_ip(request))
