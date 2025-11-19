from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.model_profile import ModelProfile
from app.schemas.model_profile import ModelProfileCreate, ModelProfileUpdate


class ModelProfileService:
    """Service for managing model profiles."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_profile(self, data: ModelProfileCreate) -> ModelProfile:
        """Create a new model profile."""
        # Check if profile with same name exists
        existing = self.db.query(ModelProfile).filter(
            ModelProfile.name == data.name
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Model profile '{data.name}' already exists"
            )
        
        profile = ModelProfile(
            name=data.name,
            suggested_min_vram_gb=data.suggested_min_vram_gb,
            suggested_batch_size=data.suggested_batch_size,
            category=data.category
        )
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile
    
    def get_profile(self, profile_id: int) -> ModelProfile:
        """Get a specific model profile by ID."""
        profile = self.db.query(ModelProfile).filter(
            ModelProfile.id == profile_id
        ).first()
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Model profile not found"
            )
        return profile
    
    def get_profile_by_name(self, name: str) -> Optional[ModelProfile]:
        """Get a model profile by name."""
        return self.db.query(ModelProfile).filter(
            ModelProfile.name == name
        ).first()
    
    def list_profiles(self) -> List[ModelProfile]:
        """List all model profiles."""
        return self.db.query(ModelProfile).all()
    
    def update_profile(
        self,
        profile_id: int,
        data: ModelProfileUpdate
    ) -> ModelProfile:
        """Update a model profile."""
        profile = self.get_profile(profile_id)
        
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(profile, field, value)
        
        self.db.commit()
        self.db.refresh(profile)
        return profile
    
    def delete_profile(self, profile_id: int) -> None:
        """Delete a model profile."""
        profile = self.get_profile(profile_id)
        self.db.delete(profile)
        self.db.commit()
