"""
Node management API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime
from uuid import UUID

from app.database import get_db
from app.models import Node, User, NodeMetric, Contract
from app.auth import get_current_user_flexible, get_current_active_provider
from app.api.schemas import (
    NodeRegister,
    NodeUpdate,
    NodeHeartbeat,
    NodeResponse,
    NodeDetailResponse
)

router = APIRouter(prefix="/api/nodes", tags=["Nodes"])


@router.post("/register", response_model=NodeResponse, status_code=status.HTTP_201_CREATED)
async def register_node(
    node_data: NodeRegister,
    current_user: User = Depends(get_current_user_flexible),
    db: Session = Depends(get_db)
):
    """
    Register a new node (provider-side)

    Args:
        node_data: Node registration data
        current_user: Authenticated user
        db: Database session

    Returns:
        Created node information
    """
    # Create new node
    new_node = Node(
        node_type=node_data.node_type,
        name=node_data.name,
        owner_id=current_user.id,
        region=node_data.region,
        latitude=node_data.latitude,
        longitude=node_data.longitude,
        total_ram_gb=node_data.total_ram_gb,
        available_ram_gb=node_data.total_ram_gb,  # Initially all available
        total_vram_gb=node_data.total_vram_gb,
        available_vram_gb=node_data.total_vram_gb,  # Initially all available
        bandwidth_mbps=node_data.bandwidth_mbps,
        base_latency_ms=node_data.base_latency_ms,
        price_per_gb_sec=node_data.price_per_gb_sec,
        metadata=node_data.metadata,
        last_heartbeat=datetime.utcnow()
    )

    db.add(new_node)
    db.commit()
    db.refresh(new_node)

    return NodeResponse.model_validate(new_node)


@router.post("/{node_id}/heartbeat", status_code=status.HTTP_200_OK)
async def node_heartbeat(
    node_id: UUID,
    metrics: NodeHeartbeat,
    current_user: User = Depends(get_current_user_flexible),
    db: Session = Depends(get_db)
):
    """
    Node reports metrics every 60 seconds

    Args:
        node_id: Node UUID
        metrics: Current node metrics
        current_user: Authenticated user
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException: If node not found or unauthorized
    """
    # Find node
    node = db.query(Node).filter(Node.id == node_id).first()
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Node not found"
        )

    # Verify ownership (unless admin)
    if current_user.role != "admin" and node.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this node"
        )

    # Update node metrics
    node.available_ram_gb = metrics.available_ram_gb
    node.available_vram_gb = metrics.available_vram_gb
    node.last_heartbeat = datetime.utcnow()

    # Update location if provided
    if metrics.latitude is not None:
        node.latitude = metrics.latitude
    if metrics.longitude is not None:
        node.longitude = metrics.longitude

    # Record metric history
    metric_record = NodeMetric(
        node_id=node_id,
        available_ram_gb=metrics.available_ram_gb,
        available_vram_gb=metrics.available_vram_gb,
        cpu_usage_pct=metrics.cpu_usage_pct,
        gpu_usage_pct=metrics.gpu_usage_pct,
        temperature_c=metrics.temperature_c,
        bandwidth_mbps=metrics.bandwidth_mbps,
        latitude=metrics.latitude,
        longitude=metrics.longitude
    )

    db.add(metric_record)
    db.commit()

    return {
        "status": "success",
        "message": "Heartbeat received",
        "node_id": str(node_id)
    }


@router.get("", response_model=List[NodeResponse])
async def list_nodes(
    node_type: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    min_ram: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0),
    db: Session = Depends(get_db)
):
    """
    List all nodes with optional filters

    Args:
        node_type: Filter by node type
        region: Filter by region
        min_ram: Minimum RAM in GB
        status: Filter by status
        limit: Maximum results
        offset: Results offset
        db: Database session

    Returns:
        List of nodes
    """
    query = db.query(Node)

    # Apply filters
    if node_type:
        query = query.filter(Node.node_type == node_type)
    if region:
        query = query.filter(Node.region == region)
    if min_ram:
        query = query.filter(Node.available_ram_gb >= min_ram)
    if status:
        query = query.filter(Node.status == status)

    # Get results
    nodes = query.offset(offset).limit(limit).all()

    return [NodeResponse.model_validate(node) for node in nodes]


@router.get("/{node_id}", response_model=NodeDetailResponse)
async def get_node_detail(
    node_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get detailed node information including earnings

    Args:
        node_id: Node UUID
        db: Database session

    Returns:
        Detailed node information

    Raises:
        HTTPException: If node not found
    """
    node = db.query(Node).filter(Node.id == node_id).first()
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Node not found"
        )

    # Calculate earnings from completed contracts
    total_earnings = db.query(func.sum(Contract.total_cost_usd)).filter(
        Contract.node_id == node_id,
        Contract.status == 'completed'
    ).scalar() or 0

    # Count contracts
    active_contracts = db.query(func.count(Contract.id)).filter(
        Contract.node_id == node_id,
        Contract.status == 'active'
    ).scalar() or 0

    total_contracts = db.query(func.count(Contract.id)).filter(
        Contract.node_id == node_id
    ).scalar() or 0

    # Build response
    node_dict = NodeResponse.model_validate(node).model_dump()
    node_dict.update({
        'total_earnings': total_earnings,
        'active_contracts': active_contracts,
        'total_contracts': total_contracts
    })

    return NodeDetailResponse(**node_dict)


@router.put("/{node_id}", response_model=NodeResponse)
async def update_node(
    node_id: UUID,
    update_data: NodeUpdate,
    current_user: User = Depends(get_current_user_flexible),
    db: Session = Depends(get_db)
):
    """
    Update node configuration

    Args:
        node_id: Node UUID
        update_data: Fields to update
        current_user: Authenticated user
        db: Database session

    Returns:
        Updated node

    Raises:
        HTTPException: If node not found or unauthorized
    """
    node = db.query(Node).filter(Node.id == node_id).first()
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Node not found"
        )

    # Verify ownership
    if current_user.role != "admin" and node.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this node"
        )

    # Update fields
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(node, field, value)

    node.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(node)

    return NodeResponse.model_validate(node)


@router.delete("/{node_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_node(
    node_id: UUID,
    current_user: User = Depends(get_current_user_flexible),
    db: Session = Depends(get_db)
):
    """
    Deactivate a node

    Args:
        node_id: Node UUID
        current_user: Authenticated user
        db: Database session

    Raises:
        HTTPException: If node not found or unauthorized
    """
    node = db.query(Node).filter(Node.id == node_id).first()
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Node not found"
        )

    # Verify ownership
    if current_user.role != "admin" and node.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this node"
        )

    # Deactivate instead of deleting
    node.status = 'offline'
    db.commit()

    return None
