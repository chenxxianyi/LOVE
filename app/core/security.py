"""
Security utilities for password hashing and token generation.
"""
import hashlib
import secrets
import uuid
from datetime import datetime, timedelta
from typing import Optional, Tuple

from app.core.config import settings


def generate_access_token() -> str:
    """Generate a secure access token."""
    return secrets.token_urlsafe(32)


def generate_refresh_token() -> str:
    """Generate a secure refresh token."""
    return secrets.token_urlsafe(48)


def hash_token(token: str) -> str:
    """Hash a token for storage. Tokens should be stored as hashes for security."""
    return hashlib.sha256(token.encode()).hexdigest()


def hash_password(password: str) -> str:
    """
    Hash a password using SHA256 with salt.
    Note: For production, consider using passlib with bcrypt.
    """
    salt = settings.PASSWORD_SALT
    combined = f"{salt}{password}"
    return hashlib.sha256(combined.encode()).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash."""
    return hash_password(password) == password_hash


def create_session_pair(user_id: int) -> Tuple[str, str, datetime, datetime]:
    """
    Create access and refresh tokens with expiration times.
    Returns: (access_token, refresh_token, access_expires_at, refresh_expires_at)
    """
    access_token = generate_access_token()
    refresh_token = generate_refresh_token()

    now = datetime.now()
    access_expires_at = now + timedelta(minutes=settings.ACCESS_TOKEN_TTL_MINUTES)
    refresh_expires_at = now + timedelta(days=settings.REFRESH_TOKEN_TTL_DAYS)

    return access_token, refresh_token, access_expires_at, refresh_expires_at


def generate_invite_code(length: int = 8) -> str:
    """Generate a random invite code."""
    return secrets.token_urlsafe(length)[:length].upper()


def generate_verify_code(length: int = 6) -> str:
    """Generate a numeric verification code."""
    return "".join(secrets.choice("0123456789") for _ in range(length))


def generate_uuid() -> str:
    """Generate a UUID string."""
    return str(uuid.uuid4())


def is_token_expired(expires_at: datetime) -> bool:
    """Check if a token has expired."""
    return datetime.now() > expires_at


def calculate_expiry(minutes: int = None, days: int = None) -> datetime:
    """Calculate expiration datetime from now."""
    now = datetime.now()
    if minutes:
        return now + timedelta(minutes=minutes)
    if days:
        return now + timedelta(days=days)
    return now + timedelta(minutes=settings.ACCESS_TOKEN_TTL_MINUTES)