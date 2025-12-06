"""
Security Headers Middleware
Adds security-related HTTP headers to all responses
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all HTTP responses
    
    Headers added:
    - Strict-Transport-Security (HSTS): Force HTTPS
    - X-Content-Type-Options: Prevent MIME sniffing
    - X-Frame-Options: Prevent clickjacking
    - X-XSS-Protection: Enable XSS filter
    - Content-Security-Policy: Control resource loading
    - Referrer-Policy: Control referrer information
    - Permissions-Policy: Control browser features
    """
    
    def __init__(
        self,
        app: ASGIApp,
        hsts_max_age: int = 31536000,  # 1 year
        enable_csp: bool = True,
        csp_directives: dict = None
    ):
        super().__init__(app)
        self.hsts_max_age = hsts_max_age
        self.enable_csp = enable_csp
        self.csp_directives = csp_directives or self._default_csp_directives()
    
    def _default_csp_directives(self) -> dict:
        """Default Content Security Policy directives"""
        return {
            "default-src": ["'self'"],
            "script-src": ["'self'", "'unsafe-inline'", "'unsafe-eval'"],  # Adjust based on needs
            "style-src": ["'self'", "'unsafe-inline'"],
            "img-src": ["'self'", "data:", "https:"],
            "font-src": ["'self'", "data:"],
            "connect-src": ["'self'"],
            "frame-ancestors": ["'none'"],
            "base-uri": ["'self'"],
            "form-action": ["'self'"]
        }
    
    def _build_csp_header(self) -> str:
        """Build Content-Security-Policy header value"""
        directives = []
        for directive, sources in self.csp_directives.items():
            sources_str = " ".join(sources)
            directives.append(f"{directive} {sources_str}")
        return "; ".join(directives)
    
    async def dispatch(self, request: Request, call_next):
        """Add security headers to response"""
        response = await call_next(request)
        
        # HSTS: Force HTTPS for all future requests
        response.headers["Strict-Transport-Security"] = (
            f"max-age={self.hsts_max_age}; includeSubDomains; preload"
        )
        
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # Enable XSS filter (legacy browsers)
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Content Security Policy
        if self.enable_csp:
            response.headers["Content-Security-Policy"] = self._build_csp_header()
        
        # Control referrer information
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Control browser features (Permissions Policy)
        response.headers["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=(), "
            "usb=(), "
            "magnetometer=(), "
            "gyroscope=(), "
            "accelerometer=()"
        )
        
        # Remove server header to avoid information disclosure
        if "server" in response.headers:
            del response.headers["server"]
        
        # Remove X-Powered-By header if present
        if "x-powered-by" in response.headers:
            del response.headers["x-powered-by"]
        
        return response


def get_security_headers_middleware(
    hsts_max_age: int = 31536000,
    enable_csp: bool = True,
    custom_csp: dict = None
) -> SecurityHeadersMiddleware:
    """
    Factory function to create security headers middleware
    
    Args:
        hsts_max_age: HSTS max-age in seconds (default: 1 year)
        enable_csp: Enable Content Security Policy (default: True)
        custom_csp: Custom CSP directives (optional)
    
    Returns:
        SecurityHeadersMiddleware instance
    """
    return SecurityHeadersMiddleware(
        app=None,  # Will be set by FastAPI
        hsts_max_age=hsts_max_age,
        enable_csp=enable_csp,
        csp_directives=custom_csp
    )
