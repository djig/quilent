from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

# Create limiter instance
limiter = Limiter(key_func=get_remote_address)


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Custom handler for rate limit exceeded"""
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Too many requests. Please try again later.",
            "retry_after": exc.detail,
        },
    )


# Rate limit decorators for different endpoints
# Usage: @limiter.limit("5/minute")
AUTH_RATE_LIMIT = "10/minute"  # 10 requests per minute for auth endpoints
API_RATE_LIMIT = "100/minute"  # 100 requests per minute for general API
