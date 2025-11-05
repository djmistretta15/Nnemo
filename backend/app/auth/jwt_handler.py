"""
JWT authentication handler
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token

    Args:
        data: Dictionary containing claims to encode
        expires_delta: Optional expiration time delta

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """
    Verify and decode JWT token

    Args:
        token: JWT token string

    Returns:
        Decoded payload dictionary or None if invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def decode_token(token: str) -> Optional[str]:
    """
    Decode token and extract user_id

    Args:
        token: JWT token string

    Returns:
        User ID from token or None
    """
    payload = verify_token(token)
    if payload:
        return payload.get("sub")
    return None
