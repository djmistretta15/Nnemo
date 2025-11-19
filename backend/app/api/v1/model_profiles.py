from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_active_user
from app.schemas.model_profile import (
    ModelProfileCreate,
    ModelProfileUpdate,
    ModelProfileResponse
)
from app.services.model_profile_service import ModelProfileService
from app.models.user import User

router = APIRouter(prefix="/model-profiles", tags=["Model Profiles"])


@router.post("", response_model=ModelProfileResponse, status_code=status.HTTP_201_CREATED)
def create_model_profile(
    data: ModelProfileCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new model profile.
    """
    service = ModelProfileService(db)
    return service.create_profile(data)


@router.get("", response_model=List[ModelProfileResponse])
def list_model_profiles(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all model profiles.
    """
    service = ModelProfileService(db)
    return service.list_profiles()


@router.get("/{profile_id}", response_model=ModelProfileResponse)
def get_model_profile(
    profile_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific model profile.
    """
    service = ModelProfileService(db)
    return service.get_profile(profile_id)


@router.patch("/{profile_id}", response_model=ModelProfileResponse)
def update_model_profile(
    profile_id: int,
    data: ModelProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update a model profile.
    """
    service = ModelProfileService(db)
    return service.update_profile(profile_id, data)


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_model_profile(
    profile_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a model profile.
    """
    service = ModelProfileService(db)
    service.delete_profile(profile_id)
    return None
