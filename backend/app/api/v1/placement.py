from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_active_user
from app.schemas.placement import (
    PlacementRequestCreate,
    PlacementFullResponse,
    PlacementRequestResponse,
    PlacementDecisionWithNode
)
from app.services.placement_service import PlacementService
from app.models.user import User
from app.models.placement_request import PlacementRequest
from app.models.placement_decision import PlacementDecision

router = APIRouter(prefix="/placement", tags=["Placement"])


@router.post("/requests", response_model=PlacementFullResponse, status_code=status.HTTP_201_CREATED)
def create_placement_request(
    data: PlacementRequestCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new placement request and get the chosen node.
    
    The system will:
    1. Determine VRAM requirements (from model profile or explicit value)
    2. Find candidate nodes
    3. Score nodes based on VRAM headroom, bandwidth, and latency
    4. Return the best match with reasoning
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User must belong to an organization"
        )
    
    placement_service = PlacementService(db)
    decision = placement_service.create_placement(
        user_id=current_user.id,
        organization_id=current_user.organization_id,
        model_name=data.model_name,
        required_vram_gb=data.required_vram_gb,
        preferred_region=data.preferred_region,
        priority=data.priority
    )
    
    # Refresh to get related data
    db.refresh(decision)
    
    # Build response
    return {
        "request": decision.request,
        "decision": {
            **{
                "id": decision.id,
                "placement_request_id": decision.placement_request_id,
                "chosen_node_id": decision.chosen_node_id,
                "reason": decision.reason,
                "estimated_fit_score": decision.estimated_fit_score,
                "created_at": decision.created_at
            },
            "node": decision.node
        }
    }


@router.get("/requests", response_model=List[PlacementRequestResponse])
def list_placement_requests(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all placement requests for the current user's organization.
    """
    requests = db.query(PlacementRequest).filter(
        PlacementRequest.organization_id == current_user.organization_id
    ).order_by(PlacementRequest.created_at.desc()).all()
    
    return requests


@router.get("/requests/{request_id}", response_model=PlacementFullResponse)
def get_placement_request(
    request_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get details of a specific placement request.
    """
    request = db.query(PlacementRequest).filter(
        PlacementRequest.id == request_id,
        PlacementRequest.organization_id == current_user.organization_id
    ).first()
    
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Placement request not found"
        )
    
    decision = db.query(PlacementDecision).filter(
        PlacementDecision.placement_request_id == request_id
    ).first()
    
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Placement decision not found"
        )
    
    return {
        "request": request,
        "decision": {
            **{
                "id": decision.id,
                "placement_request_id": decision.placement_request_id,
                "chosen_node_id": decision.chosen_node_id,
                "reason": decision.reason,
                "estimated_fit_score": decision.estimated_fit_score,
                "created_at": decision.created_at
            },
            "node": decision.node
        }
    }
