from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class NodeTelemetry(Base):
    """Node telemetry model for tracking VRAM and utilization metrics."""
    __tablename__ = "node_telemetry"
    
    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(Integer, ForeignKey("nodes.id"), nullable=False, index=True)
    vram_gb_free = Column(Float, nullable=False)
    utilization_percent = Column(Float, nullable=False)
    temperature_c = Column(Float, nullable=True)
    collected_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    node = relationship("Node", back_populates="telemetries")
    
    def __repr__(self):
        return f"<NodeTelemetry node_id={self.node_id} vram_free={self.vram_gb_free}GB>"
