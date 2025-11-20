from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_active_user
from app.schemas.node import NodeCreate, NodeUpdate, NodeResponse
from app.services.node_service import NodeService
from app.models.user import User

router = APIRouter(prefix="/nodes", tags=["Nodes"])


@router.post("", response_model=NodeResponse, status_code=status.HTTP_201_CREATED)
def create_node(
    data: NodeCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new GPU node.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User must belong to an organization"
        )
    
    node_service = NodeService(db)
    return node_service.create_node(current_user.organization_id, data)


@router.get("", response_model=List[NodeResponse])
def list_nodes(
    region: Optional[str] = Query(None, description="Filter by region"),
    provider: Optional[str] = Query(None, description="Filter by provider"),
    active: Optional[bool] = Query(None, description="Filter by active status"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all nodes with optional filters.
    """
    node_service = NodeService(db)
    return node_service.list_nodes(
        organization_id=current_user.organization_id,
        region=region,
        provider=provider,
        active=active
    )


@router.get("/{node_id}", response_model=NodeResponse)
def get_node(
    node_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get details of a specific node.
    """
    node_service = NodeService(db)
    return node_service.get_node(node_id, current_user.organization_id)


@router.patch("/{node_id}", response_model=NodeResponse)
def update_node(
    node_id: int,
    data: NodeUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update a node's configuration.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User must belong to an organization"
        )
    
    node_service = NodeService(db)
    return node_service.update_node(node_id, current_user.organization_id, data)


@router.delete("/{node_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_node(
    node_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Deactivate a node.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User must belong to an organization"
        )
    
    node_service = NodeService(db)
    node_service.delete_node(node_id, current_user.organization_id)
    return None
