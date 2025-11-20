"""
Schemas package - Pydantic models for request/response validation.
"""

from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserInDB
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, RefreshTokenRequest
from app.schemas.node import NodeCreate, NodeUpdate, NodeResponse
from app.schemas.telemetry import TelemetryCreate, TelemetryResponse
from app.schemas.model_profile import ModelProfileCreate, ModelProfileUpdate, ModelProfileResponse
from app.schemas.placement import (
    PlacementRequestCreate,
    PlacementRequestResponse,
    PlacementDecisionResponse,
    PlacementDecisionWithNode,
    PlacementFullResponse,
    PlacementQuoteRequest,
    PlacementQuoteResponse,
)

__all__ = [
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserInDB",
    "LoginRequest",
    "RegisterRequest",
    "TokenResponse",
    "RefreshTokenRequest",
    "NodeCreate",
    "NodeUpdate",
    "NodeResponse",
    "TelemetryCreate",
    "TelemetryResponse",
    "ModelProfileCreate",
    "ModelProfileUpdate",
    "ModelProfileResponse",
    "PlacementRequestCreate",
    "PlacementRequestResponse",
    "PlacementDecisionResponse",
    "PlacementDecisionWithNode",
    "PlacementFullResponse",
    "PlacementQuoteRequest",
    "PlacementQuoteResponse",
]
