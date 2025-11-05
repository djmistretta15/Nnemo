"""
Authentication package
"""

from app.auth.jwt_handler import (
    hash_password,
    verify_password,
    create_access_token,
    verify_token,
    decode_token
)

from app.auth.dependencies import (
    get_current_user,
    get_user_from_api_key,
    get_current_user_flexible,
    get_current_active_provider,
    get_current_admin
)

__all__ = [
    "hash_password",
    "verify_password",
    "create_access_token",
    "verify_token",
    "decode_token",
    "get_current_user",
    "get_user_from_api_key",
    "get_current_user_flexible",
    "get_current_active_provider",
    "get_current_admin"
]
