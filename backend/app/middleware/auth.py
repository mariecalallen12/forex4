"""
Middleware cho Authentication và Rate Limiting
DB-based authentication thay thế Firebase-style
"""

import os
import time
import asyncio
from typing import Optional, Dict, Any
from fastapi import HTTPException, Request, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from ..core.security import verify_access_token, verify_refresh_token, create_access_token, create_refresh_token
from ..core.config import settings
from ..db.session import get_db
from ..db.redis_client import get_redis, RedisCache
from ..models.user import User
from ..services.user_service import UserService

# Rate limiting configuration
RATE_LIMITS = {
    "login": {"requests": 5, "window": 900},  # 5 requests per 15 minutes
    "register": {"requests": 3, "window": 3600},  # 3 requests per hour
    "login_failed": {"requests": 3, "window": 900},  # 3 failed attempts per 15 minutes
    "general": {"requests": 100, "window": 3600},  # 100 requests per hour
}

security = HTTPBearer()

class AuthenticationError(HTTPException):
    """Custom exception for authentication errors"""
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )

class RateLimitError(HTTPException):
    """Custom exception for rate limiting errors"""
    def __init__(self, detail: str = "Rate limit exceeded"):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
        )

class TokenValidationError(HTTPException):
    """Custom exception for token validation errors"""
    def __init__(self, detail: str = "Invalid token"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )

# ========== RATE LIMITING FUNCTIONS ==========

async def rate_limit(client_ip: str, endpoint: str, cache: Optional[RedisCache] = None) -> None:
    """
    Rate limiting function - DB-based với Redis hoặc in-memory fallback
    """
    # In-memory rate limiting fallback (simple dict)
    if not hasattr(rate_limit, '_memory_store'):
        rate_limit._memory_store = {}
        rate_limit._memory_timestamps = {}
    
    try:
        # Get rate limit config
        config = RATE_LIMITS.get(endpoint, RATE_LIMITS["general"])
        max_requests = config["requests"]
        window_seconds = config["window"]
        
        # Create key
        key = f"rate_limit:{endpoint}:{client_ip}"
        current_time = time.time()
        
        # Try Redis first if available
        if cache:
            try:
                current_requests = cache.get(key)
                if current_requests is None:
                    cache.set(key, "1", ex=window_seconds)
                    return
                else:
                    current_requests = int(current_requests)
                    if current_requests >= max_requests:
                        raise RateLimitError(
                            detail=f"Quá nhiều yêu cầu. Vui lòng thử lại sau {window_seconds // 60} phút."
                        )
                    cache.incr(key)
                    return
            except Exception:
                # Fallback to memory if Redis fails
                pass
        
        # In-memory fallback
        if key in rate_limit._memory_store:
            # Check if window expired
            if current_time - rate_limit._memory_timestamps[key] > window_seconds:
                # Reset window
                rate_limit._memory_store[key] = 1
                rate_limit._memory_timestamps[key] = current_time
            else:
                rate_limit._memory_store[key] += 1
                if rate_limit._memory_store[key] > max_requests:
                    raise RateLimitError(
                        detail=f"Quá nhiều yêu cầu. Vui lòng thử lại sau {window_seconds // 60} phút."
                    )
        else:
            rate_limit._memory_store[key] = 1
            rate_limit._memory_timestamps[key] = current_time
        
        # Cleanup old entries (simple cleanup every 100 calls)
        if len(rate_limit._memory_store) > 1000:
            cutoff_time = current_time - 3600  # 1 hour
            keys_to_remove = [
                k for k, ts in rate_limit._memory_timestamps.items()
                if ts < cutoff_time
            ]
            for k in keys_to_remove:
                rate_limit._memory_store.pop(k, None)
                rate_limit._memory_timestamps.pop(k, None)
        
    except RateLimitError:
        raise
    except Exception as e:
        print(f"Rate limiting error: {e}")
        # Continue if rate limiting fails
        return

async def check_rate_limit(client_ip: str, endpoint: str, cache: Optional[RedisCache] = None) -> Dict[str, Any]:
    """
    Check current rate limit status
    """
    config = RATE_LIMITS.get(endpoint, RATE_LIMITS["general"])
    key = f"rate_limit:{endpoint}:{client_ip}"
    
    try:
        # Try Redis first
        if cache:
            try:
                current_requests = cache.get(key)
                current_requests = int(current_requests) if current_requests else 0
                ttl = cache.ttl(key)
                
                return {
                    "current_requests": current_requests,
                    "max_requests": config["requests"],
                    "window_seconds": config["window"],
                    "remaining_requests": max(0, config["requests"] - current_requests),
                    "reset_in_seconds": max(0, ttl) if ttl > 0 else config["window"]
                }
            except Exception:
                pass
        
        # In-memory fallback
        if hasattr(rate_limit, '_memory_store') and key in rate_limit._memory_store:
            current_requests = rate_limit._memory_store.get(key, 0)
            timestamp = rate_limit._memory_timestamps.get(key, time.time())
            elapsed = time.time() - timestamp
            reset_in_seconds = max(0, config["window"] - int(elapsed))
            
            return {
                "current_requests": current_requests,
                "max_requests": config["requests"],
                "window_seconds": config["window"],
                "remaining_requests": max(0, config["requests"] - current_requests),
                "reset_in_seconds": reset_in_seconds
            }
        
        return {
            "current_requests": 0,
            "max_requests": config["requests"],
            "window_seconds": config["window"],
            "remaining_requests": config["requests"],
            "reset_in_seconds": config["window"]
        }
        
    except Exception as e:
        print(f"Rate limit check error: {e}")
        return {
            "current_requests": 0,
            "max_requests": config["requests"],
            "window_seconds": config["window"],
        }

# ========== JWT TOKEN FUNCTIONS ==========

def create_access_token_for_user(user: User) -> str:
    """
    Tạo JWT access token từ User object
    """
    from ..models.user import Role
    
    # Get role name
    role_name = None
    if user.role:
        role_name = user.role.name
    elif user.role_id:
        # Fallback: query role if not loaded
        pass  # Will be handled in endpoint with DB session
    
    payload = {
        "sub": str(user.id),  # Subject (user ID)
        "email": user.email,
        "role": role_name or "customer",
        "email_verified": user.email_verified,
        "kyc_status": user.kyc_status,
    }
    
    return create_access_token(payload)

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify JWT token sử dụng app/core/security.py
    """
    return verify_access_token(token)

# ========== AUTHENTICATION HELPERS ==========

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user từ token - DB-based
    """
    token = credentials.credentials
    payload = verify_token(token)
    
    if not payload:
        raise AuthenticationError("Token không hợp lệ hoặc đã hết hạn")
    
    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationError("Token không chứa thông tin người dùng")
    
    # Query user from database
    user_service = UserService(db, None)
    user = user_service.get_by_id(int(user_id))
    
    if not user:
        raise AuthenticationError("Người dùng không tồn tại")
    
    if user.status == "deleted":
        raise AuthenticationError("Tài khoản đã bị xóa")
    
    if user.status == "suspended":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản đã bị tạm khóa"
        )
    
    return user

async def get_current_user_optional(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    """
    Get current user if authenticated (optional) - DB-based
    """
    try:
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        
        token = auth_header.split(" ")[1]
        payload = verify_token(token)
        
        if not payload:
            return None
        
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        user_service = UserService(db, None)
        user = user_service.get_by_id(int(user_id))
        
        return user
        
    except Exception:
        return None

def get_client_ip(request: Request) -> str:
    """
    Get client IP address - tương tự Next.js
    """
    # Check for forwarded headers first (for proxies/load balancers)
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        # Take the first IP if multiple IPs are present
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip
    
    # Fallback to client host
    client_host = getattr(request.client, "host", "unknown")
    return client_host if client_host else "unknown"

# ========== REFFERAL TOKEN EXTRACTION ==========

def extract_referral_token(request: Request) -> Optional[str]:
    """
    Extract referral token from request - tương tự Next.js extractReferralToken
    """
    # Check query parameters
    ref_token = request.query_params.get("ref")
    if ref_token:
        return ref_token
    
    # Check headers
    ref_header = request.headers.get("x-referral-token")
    if ref_header:
        return ref_header
    
    # Check cookies
    ref_cookie = request.cookies.get("referral_token")
    if ref_cookie:
        return ref_cookie
    
    return None

# ========== AUTHENTICATION FUNCTIONS (DB-based) ==========

async def authenticate_user(email: str, password: str, db: Session) -> Optional[User]:
    """
    Authenticate user với email và password - DB-based
    
    Returns:
        User nếu authentication thành công, None nếu không
    """
    from ..core.security import verify_password
    
    user_service = UserService(db, None)
    user = user_service.get_by_email(email.lower())
    
    if not user:
        return None
    
    # Check if account is locked
    if user.account_locked_until and user.account_locked_until > datetime.utcnow():
        raise AuthenticationError(f"Tài khoản đã bị khóa đến {user.account_locked_until}")
    
    # Verify password
    if not verify_password(password, user.password_hash):
        # Increment failed login attempts
        user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
        
        # Lock account after 5 failed attempts
        if user.failed_login_attempts >= 5:
            user.account_locked_until = datetime.utcnow() + timedelta(minutes=30)
        
        db.commit()
        return None
    
    # Reset failed login attempts on successful login
    user.failed_login_attempts = 0
    user.account_locked_until = None
    user.last_login_at = datetime.utcnow()
    db.commit()
    
    return user

async def revoke_refresh_token(token: str, db: Session = None, cache: RedisCache = None) -> None:
    """
    Revoke refresh token - DB-based hoặc Redis
    """
    # This will be implemented in refresh token storage
    # For now, just mark token as revoked in cache if available
    if cache:
        cache.set(f"revoked_token:{token}", "1", ex=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400)

# ========== EMAIL FUNCTIONS ==========

async def send_email(email_data: Dict[str, Any]) -> bool:
    """
    Send email using SendGrid - tương tự Next.js sendEmail
    """
    # TODO: Implement SendGrid integration
    # Placeholder implementation
    print(f"Sending email to {email_data.get('to')}")
    print(f"Subject: {email_data.get('subject')}")
    print(f"Template: {email_data.get('template')}")
    print(f"Data: {email_data.get('data')}")
    return True

# ========== UTILITY FUNCTIONS ==========

def get_error_message(error: Exception, error_type: str = "general") -> str:
    """
    Get appropriate error message based on error type - tương tự Next.js error handling
    """
    error_messages = {
        "auth": {
            "user-not-found": "Tài khoản không tồn tại",
            "wrong-password": "Mật khẩu không đúng",
            "email-already-in-use": "Email đã được sử dụng",
            "invalid-email": "Email không hợp lệ",
            "weak-password": "Mật khẩu quá yếu",
            "too-many-requests": "Quá nhiều lần đăng nhập thất bại. Vui lòng thử lại sau",
            "user-disabled": "Tài khoản đã bị vô hiệu hóa",
        },
        "validation": {
            "invalid-input": "Dữ liệu đầu vào không hợp lệ",
            "required-field": "Trường dữ liệu bắt buộc",
        }
    }
    
    if hasattr(error, "code"):
        return error_messages.get(error_type, {}).get(error.code, "Đã xảy ra lỗi")

# ========== ADMIN ROLE FUNCTIONS ==========

def require_admin_role(user: User, db: Session = None) -> bool:
    """
    Check if user has admin role - DB-based
    Query từ database để verify role
    """
    from ..models.user import Role
    
    # Get role from user object
    if user.role:
        role_name = user.role.name
    elif user.role_id and db:
        # Query role if not loaded
        role = db.query(Role).filter(Role.id == user.role_id).first()
        role_name = role.name if role else None
    else:
        return False
    
    # Admin roles
    admin_roles = ["admin", "owner"]
    
    return role_name in admin_roles if role_name else False
