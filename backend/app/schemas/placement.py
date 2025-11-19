from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.placement_request import PlacementPriority
from app.schemas.node import NodeResponse


class PlacementRequestCreate(BaseModel):
    """Schema for creating a placement request."""
    model_name: str = Field(..., min_length=1)
    required_vram_gb: Optional[float] = Field(None, gt=0)
    preferred_region: Optional[str] = None
    priority: PlacementPriority = PlacementPriority.normal


class PlacementRequestResponse(BaseModel):
    """Schema for placement request response."""
    id: int
    user_id: int
    organization_id: int
    model_name: str
    required_vram_gb: float
    preferred_region: Optional[str]
    priority: PlacementPriority
    created_at: datetime
    
    model_config = {"from_attributes": True}


class PlacementDecisionResponse(BaseModel):
    """Schema for placement decision response."""
    id: int
    placement_request_id: int
    chosen_node_id: int
    reason: str
    estimated_fit_score: float
    created_at: datetime
    
    model_config = {"from_attributes": True}


class PlacementDecisionWithNode(PlacementDecisionResponse):
    """Schema for placement decision with node details."""
    node: NodeResponse


class PlacementFullResponse(BaseModel):
    """Schema for complete placement response (request + decision + node)."""
    request: PlacementRequestResponse
    decision: PlacementDecisionWithNode


class PlacementQuoteRequest(BaseModel):
    """Schema for public placement quote request (stateless)."""
    model_name: str = Field(..., min_length=1)
    required_vram_gb: float = Field(..., gt=0)
    preferred_region: Optional[str] = None


class PlacementQuoteResponse(BaseModel):
    """Schema for public placement quote response."""
    chosen_node: NodeResponse
    reason: str
    estimated_fit_score: float
