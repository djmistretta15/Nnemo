from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.db.base import Base, TimestampMixin


class Organization(Base, TimestampMixin):
    """Organization model representing companies/groups."""
    __tablename__ = "organizations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # Relationships
    users = relationship("User", back_populates="organization")
    nodes = relationship("Node", back_populates="organization")
    placement_requests = relationship("PlacementRequest", back_populates="organization")
    
    def __repr__(self):
        return f"<Organization {self.name}>"
