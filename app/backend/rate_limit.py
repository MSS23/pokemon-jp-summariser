"""
Redis-based rate limiting system for API abuse prevention
Implements per-IP and per-session quotas with graceful fallbacks
"""

import os
import time
import logging
import json
from typing import Optional, Dict, Any
from collections import defaultdict, deque

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

# Import shared models
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from shared.models import RateLimitInfo

class RateLimiter:
    """
    Rate limiter with Redis backend and in-memory fallback
    Supports per-IP hourly limits and concurrent request tracking
    """

    def __init__(self, redis_url: Optional[str] = None):
        """
        Initialize rate limiter

        Args:
            redis_url: Redis connection URL (None = try environment or fallback)
        """
        self.logger = logging.getLogger(__name__)
        self.redis_client = None
        self.fallback_storage = defaultdict(lambda: {"requests": deque(), "concurrent": set()})

        # Configuration
        self.default_requests_per_hour = 5
        self.default_concurrent_limit = 1
        self.window_seconds = 3600  # 1 hour

        # Try to connect to Redis
        self._init_redis(redis_url)

        self.logger.info(
            f"RateLimiter initialized with Redis: {self.redis_client is not None}"
        )

    def _init_redis(self, redis_url: Optional[str]):
        """Initialize Redis connection"""
        if not REDIS_AVAILABLE:
            self.logger.warning("Redis not available, using in-memory fallback")
            return

        try:
            # Try provided URL, then environment, then default
            url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")

            self.redis_client = redis.from_url(
                url,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                decode_responses=True
            )

            # Test connection
            self.redis_client.ping()
            self.logger.info(f"Connected to Redis at {url}")

        except Exception as e:
            self.logger.warning(f"Failed to connect to Redis: {e}, using in-memory fallback")
            self.redis_client = None

    def _get_rate_limit_key(self, bucket: str, identifier: str) -> str:
        """Generate Redis key for rate limiting"""
        return f"pokemon_vgc_api:rate_limit:{bucket}:{identifier}"

    def _get_concurrent_key(self, bucket: str, identifier: str) -> str:
        """Generate Redis key for concurrent request tracking"""
        return f"pokemon_vgc_api:concurrent:{bucket}:{identifier}"

    def _cleanup_old_requests(self, requests: deque, current_time: float):
        """Remove old requests from deque (for in-memory fallback)"""
        while requests and current_time - requests[0] > self.window_seconds:
            requests.popleft()

    def allow_request(self, bucket: str, identifier: str, max_per_hour: int = None) -> bool:
        """
        Check if request is allowed within rate limits

        Args:
            bucket: Rate limit bucket name (e.g., "analyze", "check")
            identifier: Unique identifier (typically hashed IP)
            max_per_hour: Override for hourly limit

        Returns:
            True if request is allowed, False if rate limited
        """
        max_requests = max_per_hour or self.default_requests_per_hour
        current_time = time.time()

        try:
            if self.redis_client:
                return self._allow_request_redis(bucket, identifier, max_requests, current_time)
            else:
                return self._allow_request_fallback(bucket, identifier, max_requests, current_time)

        except Exception as e:
            self.logger.error(f"Rate limit check failed: {e}")
            # On error, allow request but log the issue
            return True

    def _allow_request_redis(self, bucket: str, identifier: str, max_requests: int, current_time: float) -> bool:
        """Redis-based rate limiting"""
        key = self._get_rate_limit_key(bucket, identifier)

        with self.redis_client.pipeline() as pipe:
            # Use sliding window with Redis sorted sets
            pipe.multi()

            # Remove old entries
            pipe.zremrangebyscore(key, 0, current_time - self.window_seconds)

            # Count current requests
            pipe.zcard(key)

            # Add current request
            pipe.zadd(key, {str(current_time): current_time})

            # Set expiry
            pipe.expire(key, self.window_seconds + 60)  # Extra buffer

            results = pipe.execute()

        current_count = results[1]  # Count after cleanup

        if current_count >= max_requests:
            # Remove the request we just added since it was rejected
            self.redis_client.zrem(key, str(current_time))
            self.logger.info(f"Rate limit exceeded for {bucket}:{identifier} ({current_count}/{max_requests})")
            return False

        return True

    def _allow_request_fallback(self, bucket: str, identifier: str, max_requests: int, current_time: float) -> bool:
        """In-memory fallback rate limiting"""
        storage_key = f"{bucket}:{identifier}"
        requests = self.fallback_storage[storage_key]["requests"]

        # Clean old requests
        self._cleanup_old_requests(requests, current_time)

        if len(requests) >= max_requests:
            self.logger.info(f"Rate limit exceeded for {bucket}:{identifier} ({len(requests)}/{max_requests})")
            return False

        # Add current request
        requests.append(current_time)
        return True

    def allow_concurrent_request(self, bucket: str, identifier: str, request_id: str) -> bool:
        """
        Check if concurrent request is allowed

        Args:
            bucket: Rate limit bucket name
            identifier: Unique identifier (typically hashed IP)
            request_id: Unique request identifier

        Returns:
            True if concurrent request is allowed, False otherwise
        """
        try:
            if self.redis_client:
                return self._allow_concurrent_redis(bucket, identifier, request_id)
            else:
                return self._allow_concurrent_fallback(bucket, identifier, request_id)

        except Exception as e:
            self.logger.error(f"Concurrent limit check failed: {e}")
            return True

    def _allow_concurrent_redis(self, bucket: str, identifier: str, request_id: str) -> bool:
        """Redis-based concurrent request limiting"""
        key = self._get_concurrent_key(bucket, identifier)
        current_time = time.time()

        with self.redis_client.pipeline() as pipe:
            # Clean up old concurrent requests (older than 10 minutes)
            pipe.zremrangebyscore(key, 0, current_time - 600)

            # Check current count
            pipe.zcard(key)

            results = pipe.execute()

        current_count = results[1]

        if current_count >= self.default_concurrent_limit:
            self.logger.info(f"Concurrent limit exceeded for {bucket}:{identifier}")
            return False

        # Add current request
        self.redis_client.zadd(key, {request_id: current_time})
        self.redis_client.expire(key, 600)  # 10 minute expiry

        return True

    def _allow_concurrent_fallback(self, bucket: str, identifier: str, request_id: str) -> bool:
        """In-memory fallback concurrent request limiting"""
        storage_key = f"{bucket}:{identifier}"
        concurrent = self.fallback_storage[storage_key]["concurrent"]

        if len(concurrent) >= self.default_concurrent_limit:
            self.logger.info(f"Concurrent limit exceeded for {bucket}:{identifier}")
            return False

        concurrent.add(request_id)
        return True

    def release_concurrent_slot(self, bucket: str, identifier: str, request_id: str = None):
        """
        Release a concurrent request slot

        Args:
            bucket: Rate limit bucket name
            identifier: Unique identifier
            request_id: Request ID to release (for Redis), or None to release any (fallback)
        """
        try:
            if self.redis_client:
                key = self._get_concurrent_key(bucket, identifier)
                if request_id:
                    self.redis_client.zrem(key, request_id)
            else:
                storage_key = f"{bucket}:{identifier}"
                concurrent = self.fallback_storage[storage_key]["concurrent"]
                if request_id and request_id in concurrent:
                    concurrent.remove(request_id)
                elif concurrent:  # Remove any item if no specific ID
                    concurrent.pop()

        except Exception as e:
            self.logger.error(f"Failed to release concurrent slot: {e}")

    def get_rate_limit_info(self, bucket: str, identifier: str) -> RateLimitInfo:
        """
        Get current rate limit status for an identifier

        Args:
            bucket: Rate limit bucket name
            identifier: Unique identifier

        Returns:
            RateLimitInfo with current status
        """
        max_requests = self.default_requests_per_hour
        current_time = time.time()

        try:
            if self.redis_client:
                key = self._get_rate_limit_key(bucket, identifier)

                # Clean old entries and count current
                with self.redis_client.pipeline() as pipe:
                    pipe.zremrangebyscore(key, 0, current_time - self.window_seconds)
                    pipe.zcard(key)
                    results = pipe.execute()

                current_count = results[1]
            else:
                storage_key = f"{bucket}:{identifier}"
                requests = self.fallback_storage[storage_key]["requests"]
                self._cleanup_old_requests(requests, current_time)
                current_count = len(requests)

            remaining = max(0, max_requests - current_count)
            reset_time = int(current_time + self.window_seconds)

            return RateLimitInfo(
                allowed=remaining > 0,
                limit=max_requests,
                remaining=remaining,
                reset_time=reset_time,
                retry_after=60 if remaining == 0 else None
            )

        except Exception as e:
            self.logger.error(f"Failed to get rate limit info: {e}")
            return RateLimitInfo(
                allowed=True,
                limit=max_requests,
                remaining=max_requests,
                reset_time=int(current_time + self.window_seconds)
            )

    def reset_rate_limit(self, bucket: str, identifier: str) -> bool:
        """
        Reset rate limit for an identifier (admin function)

        Args:
            bucket: Rate limit bucket name
            identifier: Unique identifier

        Returns:
            True if reset successful, False otherwise
        """
        try:
            if self.redis_client:
                key = self._get_rate_limit_key(bucket, identifier)
                concurrent_key = self._get_concurrent_key(bucket, identifier)

                self.redis_client.delete(key, concurrent_key)
                self.logger.info(f"Reset rate limit for {bucket}:{identifier}")
                return True
            else:
                storage_key = f"{bucket}:{identifier}"
                if storage_key in self.fallback_storage:
                    del self.fallback_storage[storage_key]
                    self.logger.info(f"Reset rate limit for {bucket}:{identifier}")
                    return True

            return False

        except Exception as e:
            self.logger.error(f"Failed to reset rate limit: {e}")
            return False

    def get_global_stats(self) -> Dict[str, Any]:
        """
        Get global rate limiting statistics

        Returns:
            Dictionary with statistics
        """
        try:
            if self.redis_client:
                # Get all rate limiting keys
                keys = self.redis_client.keys("pokemon_vgc_api:rate_limit:*")
                concurrent_keys = self.redis_client.keys("pokemon_vgc_api:concurrent:*")

                active_limits = len(keys)
                active_concurrent = len(concurrent_keys)

                return {
                    "backend": "redis",
                    "active_rate_limits": active_limits,
                    "active_concurrent_requests": active_concurrent,
                    "redis_connected": True
                }
            else:
                active_limits = len(self.fallback_storage)
                total_concurrent = sum(
                    len(data["concurrent"])
                    for data in self.fallback_storage.values()
                )

                return {
                    "backend": "memory",
                    "active_rate_limits": active_limits,
                    "active_concurrent_requests": total_concurrent,
                    "redis_connected": False
                }

        except Exception as e:
            self.logger.error(f"Failed to get global stats: {e}")
            return {"error": str(e)}

    def cleanup_expired_data(self):
        """Clean up expired data (maintenance function)"""
        try:
            current_time = time.time()

            if not self.redis_client:
                # Clean up in-memory storage
                keys_to_remove = []
                for key, data in self.fallback_storage.items():
                    self._cleanup_old_requests(data["requests"], current_time)
                    if not data["requests"] and not data["concurrent"]:
                        keys_to_remove.append(key)

                for key in keys_to_remove:
                    del self.fallback_storage[key]

                self.logger.info(f"Cleaned up {len(keys_to_remove)} expired entries")

        except Exception as e:
            self.logger.error(f"Failed to cleanup expired data: {e}")