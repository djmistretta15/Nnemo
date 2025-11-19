from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.base import Base, TimestampMixin


class PlacementDecision(Base, TimestampMixin):
    """Placement decision model representing the chosen node for a placement request."""
    __tablename__ = "placement_decisions"
    
    id = Column(Integer, primary_key=True, index=True)
    placement_request_id = Column(Integer, ForeignKey("placement_requests.id"), unique=True, nullable=False)
    chosen_node_id = Column(Integer, ForeignKey("nodes.id"), nullable=False)
    reason = Column(Text, nullable=False)
    estimated_fit_score = Column(Float, nullable=False)
    
    # Relationships
    request = relationship("PlacementRequest", back_populates="decision")
    node = relationship("Node", back_populates="placement_decisions")
    
    def __repr__(self):
        return f"<PlacementDecision request_id={self.placement_request_id} node_id={self.chosen_node_id} score={self.estimated_fit_score}>"
