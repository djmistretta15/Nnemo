from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class NodeBase(BaseModel):
    """Base node schema."""
    name: str = Field(..., min_length=1)
    provider_name: str
    region: str
    gpu_model: str
    vram_gb_total: float = Field(..., gt=0)
    memory_bandwidth_gbps: Optional[float] = Field(None, gt=0)
    network_latency_ms_estimate: Optional[float] = Field(None, ge=0)


class NodeCreate(NodeBase):
    """Schema for creating a new node."""
    pass


class NodeUpdate(BaseModel):
    """Schema for updating a node."""
    name: Optional[str] = Field(None, min_length=1)
    provider_name: Optional[str] = None
    region: Optional[str] = None
    gpu_model: Optional[str] = None
    vram_gb_total: Optional[float] = Field(None, gt=0)
    memory_bandwidth_gbps: Optional[float] = Field(None, gt=0)
    network_latency_ms_estimate: Optional[float] = Field(None, ge=0)
    is_active: Optional[bool] = None


class NodeResponse(NodeBase):
    """Schema for node response."""
    id: int
    organization_id: int
    vram_gb_free_estimate: float
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}
