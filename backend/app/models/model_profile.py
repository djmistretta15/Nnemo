from sqlalchemy import Column, Integer, String, Float, Enum
from app.db.base import Base, TimestampMixin
import enum


class ModelCategory(str, enum.Enum):
    """Model profile category enumeration."""
    llm = "llm"
    diffusion = "diffusion"
    other = "other"


class ModelProfile(Base, TimestampMixin):
    """Model profile representing different AI models and their requirements."""
    __tablename__ = "model_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    suggested_min_vram_gb = Column(Float, nullable=False)
    suggested_batch_size = Column(Integer, nullable=True)
    category = Column(Enum(ModelCategory), default=ModelCategory.other, nullable=False)
    
    def __repr__(self):
        return f"<ModelProfile {self.name} ({self.category})>"
