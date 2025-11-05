"""
Contract management API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from uuid import UUID
from decimal import Decimal

from app.database import get_db
from app.models import Contract, Node, Client, User
from app.auth import get_current_user_flexible
from app.api.schemas import (
    ContractCreate,
    ContractResponse,
    ContractSettle,
    ContractExtend
)

router = APIRouter(prefix="/api/contracts", tags=["Contracts"])


@router.post("/create", response_model=ContractResponse, status_code=status.HTTP_201_CREATED)
async def create_contract(
    contract_data: ContractCreate,
    current_user: User = Depends(get_current_user_flexible),
    db: Session = Depends(get_db)
):
    """
    Create a new memory contract (allocate memory)

    Args:
        contract_data: Contract creation data
        current_user: Authenticated user
        db: Database session

    Returns:
        Created contract

    Raises:
        HTTPException: If node not available or insufficient capacity
    """
    # Get node
    node = db.query(Node).filter(
        Node.id == contract_data.node_id,
        Node.status == 'active'
    ).first()

    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Node not found or not available"
        )

    # Check capacity
    if node.available_ram_gb < contract_data.ram_gb:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient RAM. Available: {node.available_ram_gb}GB, Requested: {contract_data.ram_gb}GB"
        )

    if node.available_vram_gb < contract_data.vram_gb:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient VRAM. Available: {node.available_vram_gb}GB, Requested: {contract_data.vram_gb}GB"
        )

    # Get or create client
    client = db.query(Client).filter(Client.user_id == current_user.id).first()
    if not client:
        client = Client(
            user_id=current_user.id,
            org_name=current_user.organization or current_user.full_name or "Unknown"
        )
        db.add(client)
        db.commit()
        db.refresh(client)

    # Calculate pricing
    total_gb = contract_data.ram_gb + contract_data.vram_gb
    total_cost = (
        Decimal(str(total_gb)) *
        Decimal(str(contract_data.duration_sec)) *
        node.price_per_gb_sec
    )

    # Create contract
    start_time = datetime.utcnow()
    end_time = start_time + timedelta(seconds=contract_data.duration_sec)

    new_contract = Contract(
        client_id=client.id,
        node_id=node.id,
        ram_gb=contract_data.ram_gb,
        vram_gb=contract_data.vram_gb,
        duration_sec=contract_data.duration_sec,
        start_time=start_time,
        end_time=end_time,
        price_per_gb_sec=node.price_per_gb_sec,
        total_cost_usd=total_cost,
        status='active'
    )

    # Allocate capacity
    node.available_ram_gb -= contract_data.ram_gb
    node.available_vram_gb -= contract_data.vram_gb

    db.add(new_contract)
    db.commit()
    db.refresh(new_contract)

    return ContractResponse.model_validate(new_contract)


@router.get("", response_model=List[ContractResponse])
async def list_contracts(
    client_id: Optional[UUID] = Query(None),
    node_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0),
    current_user: User = Depends(get_current_user_flexible),
    db: Session = Depends(get_db)
):
    """
    List contracts with filters

    Args:
        client_id: Filter by client
        node_id: Filter by node
        status: Filter by status
        limit: Maximum results
        offset: Results offset
        current_user: Authenticated user
        db: Database session

    Returns:
        List of contracts
    """
    query = db.query(Contract)

    # If not admin, only show user's contracts
    if current_user.role != "admin":
        # Get user's client
        client = db.query(Client).filter(Client.user_id == current_user.id).first()
        if client:
            query = query.filter(Contract.client_id == client.id)

        # Or nodes owned by user
        user_nodes = db.query(Node.id).filter(Node.owner_id == current_user.id).all()
        if user_nodes:
            node_ids = [n.id for n in user_nodes]
            query = query.filter(
                (Contract.client_id == client.id) | (Contract.node_id.in_(node_ids))
            )

    # Apply filters
    if client_id:
        query = query.filter(Contract.client_id == client_id)
    if node_id:
        query = query.filter(Contract.node_id == node_id)
    if status:
        query = query.filter(Contract.status == status)

    # Get results
    contracts = query.order_by(Contract.created_at.desc()).offset(offset).limit(limit).all()

    return [ContractResponse.model_validate(c) for c in contracts]


@router.get("/{contract_id}", response_model=ContractResponse)
async def get_contract(
    contract_id: UUID,
    current_user: User = Depends(get_current_user_flexible),
    db: Session = Depends(get_db)
):
    """
    Get contract details

    Args:
        contract_id: Contract UUID
        current_user: Authenticated user
        db: Database session

    Returns:
        Contract details

    Raises:
        HTTPException: If contract not found or unauthorized
    """
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    # Verify access
    if current_user.role != "admin":
        client = db.query(Client).filter(Client.user_id == current_user.id).first()
        node = db.query(Node).filter(
            Node.id == contract.node_id,
            Node.owner_id == current_user.id
        ).first()

        if not client or (contract.client_id != client.id and not node):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this contract"
            )

    return ContractResponse.model_validate(contract)


@router.post("/{contract_id}/settle", response_model=ContractResponse)
async def settle_contract(
    contract_id: UUID,
    settle_data: ContractSettle,
    current_user: User = Depends(get_current_user_flexible),
    db: Session = Depends(get_db)
):
    """
    Complete contract and trigger payment

    Args:
        contract_id: Contract UUID
        settle_data: Settlement data
        current_user: Authenticated user
        db: Database session

    Returns:
        Updated contract

    Raises:
        HTTPException: If contract not found or already settled
    """
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    if contract.status != 'active':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contract is not active"
        )

    # Verify ownership (node owner or admin)
    node = db.query(Node).filter(Node.id == contract.node_id).first()
    if current_user.role != "admin" and node.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to settle this contract"
        )

    # Update contract
    contract.status = 'completed'
    contract.completed_at = datetime.utcnow()
    contract.egress_gb = settle_data.actual_egress_gb or Decimal('0')

    # Release capacity back to node
    node.available_ram_gb += contract.ram_gb
    node.available_vram_gb += contract.vram_gb

    db.commit()
    db.refresh(contract)

    return ContractResponse.model_validate(contract)


@router.post("/{contract_id}/extend", response_model=ContractResponse)
async def extend_contract(
    contract_id: UUID,
    extend_data: ContractExtend,
    current_user: User = Depends(get_current_user_flexible),
    db: Session = Depends(get_db)
):
    """
    Extend active contract duration

    Args:
        contract_id: Contract UUID
        extend_data: Extension data
        current_user: Authenticated user
        db: Database session

    Returns:
        Updated contract

    Raises:
        HTTPException: If contract not active or unauthorized
    """
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    if contract.status != 'active':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only extend active contracts"
        )

    # Verify ownership (client or admin)
    client = db.query(Client).filter(Client.user_id == current_user.id).first()
    if current_user.role != "admin" and (not client or contract.client_id != client.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to extend this contract"
        )

    # Calculate additional cost
    total_gb = contract.ram_gb + contract.vram_gb
    additional_cost = (
        Decimal(str(total_gb)) *
        Decimal(str(extend_data.additional_duration_sec)) *
        contract.price_per_gb_sec
    )

    # Extend contract
    contract.duration_sec += extend_data.additional_duration_sec
    contract.end_time += timedelta(seconds=extend_data.additional_duration_sec)
    contract.total_cost_usd += additional_cost

    db.commit()
    db.refresh(contract)

    return ContractResponse.model_validate(contract)
