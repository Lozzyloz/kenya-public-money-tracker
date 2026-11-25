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

    def _prune(self, now: float) -> None:
        if len(self.hits) > 10_000:  # drop stale keys so memory stays bounded
            stale = [k for k, q in self.hits.items() if not q or now - q[-1] > self.window]
            for key in stale:
                del self.hits[key]

    def _too_many(self, queue: deque, now: float) -> HTTPException:
        retry = int(self.window - (now - queue[0])) + 1
        return HTTPException(
            status_code=429,
            detail="Too many requests. Please try again later.",
            headers={"Retry-After": str(retry)},
        )

    def check(self, key: str) -> None:
        """Count this request and refuse it if the limit is already reached."""
        now = time.monotonic()
        with self.lock:
            self._prune(now)
            queue = self.hits[key]
            while queue and now - queue[0] > self.window:
                queue.popleft()
            if len(queue) >= self.limit:
                raise self._too_many(queue, now)
            queue.append(now)

    def raise_if_blocked(self, key: str) -> None:
        """Refuse if the limit is reached, without counting this request."""
        now = time.monotonic()
        with self.lock:
            queue = self.hits.get(key)
            if not queue:
                return
            while queue and now - queue[0] > self.window:
                queue.popleft()
            if queue and len(queue) >= self.limit:
                raise self._too_many(queue, now)

    def record(self, key: str) -> None:
        now = time.monotonic()
        with self.lock:
            self._prune(now)
            self.hits[key].append(now)

    def clear(self, key: str) -> None:
        with self.lock:
            self.hits.pop(key, None)

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
login_email_limiter = SlidingWindowLimiter(
    settings.login_fail_limit_email, settings.login_window_seconds
)
login_ip_limiter = SlidingWindowLimiter(
    settings.login_fail_limit_ip, settings.login_window_seconds
)


def limit_report_submissions(request: Request) -> None:
    report_limiter.check(client_ip(request))

