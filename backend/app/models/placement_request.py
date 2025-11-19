from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.db.base import Base, TimestampMixin
import enum


class PlacementPriority(str, enum.Enum):
    """Placement request priority enumeration."""
    normal = "normal"
    high = "high"


class PlacementRequest(Base, TimestampMixin):
    """Placement request model for GPU workload placement requests."""
    __tablename__ = "placement_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    model_name = Column(String, nullable=False)
    required_vram_gb = Column(Float, nullable=False)
    preferred_region = Column(String, nullable=True)
    priority = Column(Enum(PlacementPriority), default=PlacementPriority.normal, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="placement_requests")
    organization = relationship("Organization", back_populates="placement_requests")
    decision = relationship("PlacementDecision", back_populates="request", uselist=False)
    
    def __repr__(self):
        return f"<PlacementRequest {self.model_name} ({self.required_vram_gb}GB)>"
