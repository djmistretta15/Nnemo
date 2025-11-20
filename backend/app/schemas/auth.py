from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class LoginRequest(BaseModel):
    """Schema for login request."""
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    """Schema for registration request."""
    organization_name: str = Field(..., min_length=1)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str


class TokenResponse(BaseModel):
    """Schema for token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request."""
    refresh_token: str
