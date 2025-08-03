from datetime import datetime, timedelta
from typing import Any, Union
from jose import jwt
from passlib.context import CryptContext
import random
import string

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def generate_otp(length: int = 6) -> str:
    return ''.join(random.choices(string.digits, k=length))

# OTP Rate Limiting
OTP_LIMIT = 4  # Maximum OTP requests per module
OTP_WINDOW_HOURS = 24  # Reset window in hours

def check_otp_limit(redis_client, email: str, module: str) -> tuple[bool, int]:
    """
    Check if user has exceeded OTP limit for a specific module.
    Returns (can_request, attempts_remaining)
    """
    if not redis_client:
        return True, OTP_LIMIT
    
    key = f"otp_limit:{module}:{email}"
    current_attempts = redis_client.get(key)
    
    if current_attempts is None:
        return True, OTP_LIMIT
    
    attempts = int(current_attempts)
    if attempts >= OTP_LIMIT:
        return False, 0
    
    return True, OTP_LIMIT - attempts

def increment_otp_count(redis_client, email: str, module: str) -> None:
    """Increment OTP request count for a module."""
    if not redis_client:
        return
    
    key = f"otp_limit:{module}:{email}"
    current_attempts = redis_client.get(key)
    
    if current_attempts is None:
        # First attempt, set with expiry
        redis_client.setex(key, OTP_WINDOW_HOURS * 3600, 1)
    else:
        # Increment existing count
        redis_client.incr(key)

def reset_otp_limit(redis_client, email: str, module: str) -> None:
    """Reset OTP limit for a module (called after successful verification)."""
    if not redis_client:
        return
    
    key = f"otp_limit:{module}:{email}"
    redis_client.delete(key)

def get_otp_remaining_time(redis_client, email: str, module: str) -> int:
    """Get remaining time in seconds for OTP limit reset."""
    if not redis_client:
        return 0
    
    key = f"otp_limit:{module}:{email}"
    ttl = redis_client.ttl(key)
    return max(0, ttl) 