from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.model_profile import ModelCategory


class ModelProfileBase(BaseModel):
    """Base model profile schema."""
    name: str = Field(..., min_length=1)
    suggested_min_vram_gb: float = Field(..., gt=0)
    suggested_batch_size: Optional[int] = Field(None, gt=0)
    category: ModelCategory = ModelCategory.other


class ModelProfileCreate(ModelProfileBase):
    """Schema for creating a model profile."""
    pass


class ModelProfileUpdate(BaseModel):
    """Schema for updating a model profile."""
    name: Optional[str] = Field(None, min_length=1)
    suggested_min_vram_gb: Optional[float] = Field(None, gt=0)
    suggested_batch_size: Optional[int] = Field(None, gt=0)
    category: Optional[ModelCategory] = None


class ModelProfileResponse(ModelProfileBase):
    """Schema for model profile response."""
    id: int
    created_at: datetime
    
    model_config = {"from_attributes": True}
