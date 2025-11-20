from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base, TimestampMixin


class Node(Base, TimestampMixin):
    """GPU Node model representing compute nodes with VRAM."""
    __tablename__ = "nodes"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    name = Column(String, nullable=False, index=True)
    provider_name = Column(String, nullable=False)
    region = Column(String, nullable=False, index=True)
    gpu_model = Column(String, nullable=False)
    vram_gb_total = Column(Float, nullable=False)
    vram_gb_free_estimate = Column(Float, nullable=False)
    memory_bandwidth_gbps = Column(Float, nullable=True)
    network_latency_ms_estimate = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="nodes")
    telemetries = relationship("NodeTelemetry", back_populates="node", cascade="all, delete-orphan")
    placement_decisions = relationship("PlacementDecision", back_populates="node")
    
    def __repr__(self):
        return f"<Node {self.name} ({self.gpu_model})>"
