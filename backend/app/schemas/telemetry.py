from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TelemetryCreate(BaseModel):
    """Schema for creating telemetry data."""
    vram_gb_free: float = Field(..., ge=0)
    utilization_percent: float = Field(..., ge=0, le=100)
    temperature_c: Optional[float] = Field(None, ge=0)


class TelemetryResponse(TelemetryCreate):
    """Schema for telemetry response."""
    id: int
    node_id: int
    collected_at: datetime
    
    model_config = {"from_attributes": True}
