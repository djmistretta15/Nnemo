from typing import List
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_active_user
from app.schemas.telemetry import TelemetryCreate, TelemetryResponse
from app.services.telemetry_service import TelemetryService
from app.models.user import User

router = APIRouter(prefix="/nodes", tags=["Telemetry"])


@router.post(
    "/{node_id}/telemetry",
    response_model=TelemetryResponse,
    status_code=status.HTTP_201_CREATED
)
def create_telemetry(
    node_id: int,
    data: TelemetryCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Submit telemetry data for a node.
    Updates the node's VRAM free estimate.
    """
    telemetry_service = TelemetryService(db)
    return telemetry_service.create_telemetry(node_id, data)


@router.get(
    "/{node_id}/telemetry",
    response_model=List[TelemetryResponse]
)
def get_node_telemetry(
    node_id: int,
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get recent telemetry data for a node.
    """
    telemetry_service = TelemetryService(db)
    return telemetry_service.get_node_telemetry(node_id, limit)
