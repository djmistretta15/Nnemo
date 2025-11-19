from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.deps import get_db, verify_api_key
from app.schemas.placement import PlacementQuoteRequest, PlacementQuoteResponse
from app.services.placement_service import PlacementService

router = APIRouter(prefix="/public", tags=["Public API"])


@router.post(
    "/placement/quote",
    response_model=PlacementQuoteResponse,
    dependencies=[Depends(verify_api_key)]
)
def get_placement_quote(
    data: PlacementQuoteRequest,
    db: Session = Depends(get_db)
):
    """
    Get a placement quote without creating a placement request (stateless).
    
    Requires API key authentication via X-API-Key header.
    
    Returns the best matching node based on VRAM requirements.
    """
    placement_service = PlacementService(db)
    
    node, score, reason = placement_service.get_placement_quote(
        model_name=data.model_name,
        required_vram_gb=data.required_vram_gb,
        preferred_region=data.preferred_region
    )
    
    if not node:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"No suitable node found for {data.required_vram_gb}GB VRAM requirement"
                   + (f" in region '{data.preferred_region}'" if data.preferred_region else "")
        )
    
    return {
        "chosen_node": node,
        "reason": reason,
        "estimated_fit_score": score
    }
