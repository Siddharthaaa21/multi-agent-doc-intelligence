import asyncio
import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class SECRateLimiter:
    """
    Token bucket rate limiter compliant with SEC EDGAR automated access guidelines:
    - Maximum 10 requests per second across all endpoints.
    - Prevents 429 Too Many Requests and IP blockades.
    """

    def __init__(self, rate: float = 10.0, capacity: Optional[float] = None):
        self.rate = rate  # tokens added per second
        self.capacity = capacity if capacity is not None else rate
        self.tokens = self.capacity
        self.last_update = time.monotonic()
        self._lock = asyncio.Lock()
        
        # Telemetry
        self.total_requests = 0
        self.throttled_requests = 0
        self.total_wait_time_sec = 0.0

    async def acquire(self, tokens: float = 1.0) -> float:
        """
        Acquire tokens before making an outbound request to SEC EDGAR.
        Returns the duration waited in seconds.
        """
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self.last_update
            self.last_update = now

            # Replenish tokens based on elapsed time
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)

            wait_time = 0.0
            if self.tokens < tokens:
                needed = tokens - self.tokens
                wait_time = needed / self.rate
                self.throttled_requests += 1
                self.total_wait_time_sec += wait_time
                logger.debug(f"[SEC Rate Limiter] Throttling request: waiting {wait_time:.4f}s for SEC compliance")
                await asyncio.sleep(wait_time)
                # After waiting, replenishment has caught up
                self.tokens = 0.0
                self.last_update = time.monotonic()
            else:
                self.tokens -= tokens

            self.total_requests += 1
            return wait_time

    def get_stats(self) -> dict:
        return {
            "rate_limit_per_sec": self.rate,
            "total_requests": self.total_requests,
            "throttled_requests": self.throttled_requests,
            "total_wait_time_sec": round(self.total_wait_time_sec, 4),
            "available_tokens": round(self.tokens, 2)
        }
