from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.db.base import Base, TimestampMixin
import enum


class UserRole(str, enum.Enum):
    """User role enumeration."""
    admin = "admin"
    org_admin = "org_admin"
    viewer = "viewer"


class User(Base, TimestampMixin):
    """User model representing system users."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(Enum(UserRole), default=UserRole.viewer, nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="users")
    placement_requests = relationship("PlacementRequest", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.email}>"
