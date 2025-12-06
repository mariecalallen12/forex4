"""
Rate Limiting Middleware
Implements Redis-based rate limiting to prevent abuse
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import time
from typing import Optional
import redis
import hashlib


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using Redis for distributed rate limiting
    
    Limits:
    - 100 requests per minute per IP address
    - 1000 requests per hour per authenticated user
    """
    
    def __init__(
        self,
        app,
        redis_client: Optional[redis.Redis] = None,
        requests_per_minute: int = 100,
        requests_per_hour: int = 1000
    ):
        super().__init__(app)
        self.redis_client = redis_client
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        
    def get_client_identifier(self, request: Request) -> str:
        """Get unique identifier for the client (IP or user ID)"""
        # Try to get user ID from request state (set by auth middleware)
        if hasattr(request.state, 'user_id'):
            return f"user:{request.state.user_id}"
        
        # Fallback to IP address
        forwarded = request.headers.get('X-Forwarded-For')
        if forwarded:
            ip = forwarded.split(',')[0].strip()
        else:
            ip = request.client.host if request.client else 'unknown'
        
        return f"ip:{ip}"
    
    def get_rate_limit_key(self, identifier: str, window: str) -> str:
        """Generate Redis key for rate limiting"""
        return f"rate_limit:{identifier}:{window}"
    
    async def check_rate_limit(
        self,
        identifier: str,
        limit: int,
        window_seconds: int
    ) -> tuple[bool, int, int]:
        """
        Check if request is within rate limit
        
        Returns:
            tuple: (is_allowed, current_count, reset_time)
        """
        if not self.redis_client:
            # If Redis is not available, allow the request
            return True, 0, 0
        
        current_window = int(time.time() / window_seconds)
        key = f"{self.get_rate_limit_key(identifier, str(current_window))}"
        
        try:
            # Increment counter
            current_count = self.redis_client.incr(key)
            
            # Set expiry on first request
            if current_count == 1:
                self.redis_client.expire(key, window_seconds)
            
            # Calculate reset time
            reset_time = (current_window + 1) * window_seconds
            
            # Check if limit exceeded
            is_allowed = current_count <= limit
            
            return is_allowed, current_count, reset_time
            
        except Exception as e:
            # Log error but allow request if Redis fails
            print(f"Rate limiter error: {e}")
            return True, 0, 0
    
    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting"""
        
        # Skip rate limiting for health check endpoints
        if request.url.path in ['/health', '/api/health', '/']:
            return await call_next(request)
        
        identifier = self.get_client_identifier(request)
        
        # Check per-minute limit
        is_allowed_minute, count_minute, reset_minute = await self.check_rate_limit(
            identifier,
            self.requests_per_minute,
            60  # 1 minute
        )
        
        # Check per-hour limit
        is_allowed_hour, count_hour, reset_hour = await self.check_rate_limit(
            identifier,
            self.requests_per_hour,
            3600  # 1 hour
        )
        
        # If either limit is exceeded, return 429
        if not is_allowed_minute or not is_allowed_hour:
            limit_type = "minute" if not is_allowed_minute else "hour"
            reset_time = reset_minute if not is_allowed_minute else reset_hour
            
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "rate_limit_exceeded",
                    "message": f"Too many requests. Rate limit exceeded for {limit_type}.",
                    "retry_after": reset_time - int(time.time())
                },
                headers={
                    "Retry-After": str(reset_time - int(time.time())),
                    "X-RateLimit-Limit": str(self.requests_per_minute if limit_type == "minute" else self.requests_per_hour),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_time)
                }
            )
        
        # Add rate limit headers to response
        response = await call_next(request)
        
        # Add rate limit info to response headers
        response.headers["X-RateLimit-Limit-Minute"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining-Minute"] = str(self.requests_per_minute - count_minute)
        response.headers["X-RateLimit-Limit-Hour"] = str(self.requests_per_hour)
        response.headers["X-RateLimit-Remaining-Hour"] = str(self.requests_per_hour - count_hour)
        
        return response


def get_rate_limiter(redis_url: Optional[str] = None) -> RateLimiterMiddleware:
    """
    Factory function to create rate limiter middleware
    
    Args:
        redis_url: Redis connection URL (optional)
    
    Returns:
        RateLimiterMiddleware instance
    """
    redis_client = None
    if redis_url:
        try:
            redis_client = redis.from_url(redis_url, decode_responses=True)
        except Exception as e:
            print(f"Failed to connect to Redis for rate limiting: {e}")
    
    return RateLimiterMiddleware(
        app=None,  # Will be set by FastAPI
        redis_client=redis_client,
        requests_per_minute=100,
        requests_per_hour=1000
    )
