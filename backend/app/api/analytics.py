"""
Analytics API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Optional
from datetime import datetime, timedelta
from uuid import UUID
from decimal import Decimal

from app.database import get_db
from app.models import Node, Contract, Transaction, Client, User, NodeMetric
from app.auth import get_current_user_flexible
from app.api.schemas import (
    EarningsResponse,
    SpendingResponse,
    MarketSupplyResponse,
    PricingTrendResponse
)

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/node/{node_id}/earnings", response_model=EarningsResponse)
async def get_node_earnings(
    node_id: UUID,
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user_flexible),
    db: Session = Depends(get_db)
):
    """
    Get earnings for a specific node

    Args:
        node_id: Node UUID
        days: Number of days to analyze
        current_user: Authenticated user
        db: Database session

    Returns:
        Earnings breakdown
    """
    # Verify node exists and user owns it
    node = db.query(Node).filter(Node.id == node_id).first()
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Node not found"
        )

    if current_user.role != "admin" and node.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this node's earnings"
        )

    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    # Get total earnings
    total_earnings = db.query(func.sum(Contract.total_cost_usd)).filter(
        Contract.node_id == node_id,
        Contract.status == 'completed',
        Contract.completed_at >= start_date
    ).scalar() or Decimal('0')

    # Get earnings by period (daily)
    earnings_by_day = db.query(
        func.date(Contract.completed_at).label('date'),
        func.sum(Contract.total_cost_usd).label('earnings'),
        func.count(Contract.id).label('contracts')
    ).filter(
        Contract.node_id == node_id,
        Contract.status == 'completed',
        Contract.completed_at >= start_date
    ).group_by(
        func.date(Contract.completed_at)
    ).order_by(
        func.date(Contract.completed_at)
    ).all()

    return EarningsResponse(
        total_earnings=total_earnings,
        earnings_by_period=[
            {
                "date": row.date.isoformat(),
                "earnings": float(row.earnings),
                "contracts": row.contracts
            }
            for row in earnings_by_day
        ]
    )


@router.get("/client/{client_id}/spending", response_model=SpendingResponse)
async def get_client_spending(
    client_id: UUID,
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user_flexible),
    db: Session = Depends(get_db)
):
    """
    Get spending for a specific client

    Args:
        client_id: Client UUID
        days: Number of days to analyze
        current_user: Authenticated user
        db: Database session

    Returns:
        Spending breakdown
    """
    # Verify client exists and user owns it
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )

    if current_user.role != "admin" and client.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this client's spending"
        )

    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    # Get total spending
    total_spending = db.query(func.sum(Contract.total_cost_usd)).filter(
        Contract.client_id == client_id,
        Contract.created_at >= start_date
    ).scalar() or Decimal('0')

    # Get spending by period (daily)
    spending_by_day = db.query(
        func.date(Contract.created_at).label('date'),
        func.sum(Contract.total_cost_usd).label('spending'),
        func.count(Contract.id).label('contracts')
    ).filter(
        Contract.client_id == client_id,
        Contract.created_at >= start_date
    ).group_by(
        func.date(Contract.created_at)
    ).order_by(
        func.date(Contract.created_at)
    ).all()

    # Get spending by node type
    spending_by_type = db.query(
        Node.node_type,
        func.sum(Contract.total_cost_usd).label('spending')
    ).join(
        Contract, Contract.node_id == Node.id
    ).filter(
        Contract.client_id == client_id,
        Contract.created_at >= start_date
    ).group_by(
        Node.node_type
    ).all()

    return SpendingResponse(
        total_spending=total_spending,
        spending_by_period=[
            {
                "date": row.date.isoformat(),
                "spending": float(row.spending),
                "contracts": row.contracts
            }
            for row in spending_by_day
        ],
        spending_by_node_type={
            row.node_type: Decimal(str(row.spending))
            for row in spending_by_type
        }
    )


@router.get("/market/supply", response_model=MarketSupplyResponse)
async def get_market_supply(
    region: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get global or regional supply metrics

    Args:
        region: Optional region filter
        db: Database session

    Returns:
        Supply metrics
    """
    query = db.query(Node).filter(Node.status == 'active')

    if region:
        query = query.filter(Node.region == region)

    nodes = query.all()

    total_nodes = len(nodes)
    total_ram_gb = sum(n.total_ram_gb for n in nodes)
    available_ram_gb = sum(n.available_ram_gb for n in nodes)
    total_vram_gb = sum(n.total_vram_gb for n in nodes)
    available_vram_gb = sum(n.available_vram_gb for n in nodes)

    # Calculate utilization rate
    total_capacity = total_ram_gb + total_vram_gb
    available_capacity = available_ram_gb + available_vram_gb
    utilized_capacity = total_capacity - available_capacity

    utilization_rate = (
        Decimal(str(utilized_capacity / total_capacity * 100))
        if total_capacity > 0 else Decimal('0')
    )

    return MarketSupplyResponse(
        total_nodes=total_nodes,
        total_ram_gb=total_ram_gb,
        available_ram_gb=available_ram_gb,
        total_vram_gb=total_vram_gb,
        available_vram_gb=available_vram_gb,
        utilization_rate=utilization_rate
    )


@router.get("/market/pricing", response_model=PricingTrendResponse)
async def get_pricing_trends(
    region: Optional[str] = Query(None),
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    Get pricing trends over time

    Args:
        region: Optional region filter
        days: Number of days to analyze
        db: Database session

    Returns:
        Pricing trends
    """
    query = db.query(Node).filter(Node.status == 'active')

    if region:
        query = query.filter(Node.region == region)

    # Get current average price
    avg_price = db.query(func.avg(Node.price_per_gb_sec)).filter(
        Node.status == 'active'
    )

    if region:
        avg_price = avg_price.filter(Node.region == region)

    avg_price_result = avg_price.scalar() or Decimal('0')

    # Get historical pricing from contracts
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    price_trends = db.query(
        func.date(Contract.created_at).label('date'),
        func.avg(Contract.price_per_gb_sec).label('avg_price'),
        func.min(Contract.price_per_gb_sec).label('min_price'),
        func.max(Contract.price_per_gb_sec).label('max_price')
    ).filter(
        Contract.created_at >= start_date
    )

    if region:
        price_trends = price_trends.join(Node).filter(Node.region == region)

    price_trends = price_trends.group_by(
        func.date(Contract.created_at)
    ).order_by(
        func.date(Contract.created_at)
    ).all()

    return PricingTrendResponse(
        avg_price_per_gb_sec=avg_price_result,
        price_trends=[
            {
                "date": row.date.isoformat(),
                "avg_price": float(row.avg_price),
                "min_price": float(row.min_price),
                "max_price": float(row.max_price)
            }
            for row in price_trends
        ]
    )


@router.get("/dashboard", response_model=dict)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user_flexible),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive dashboard statistics for current user

    Args:
        current_user: Authenticated user
        db: Database session

    Returns:
        Dashboard statistics
    """
    stats = {
        "user": {
            "id": str(current_user.id),
            "email": current_user.email,
            "role": current_user.role
        }
    }

    # Provider stats
    nodes = db.query(Node).filter(Node.owner_id == current_user.id).all()
    if nodes:
        total_earnings = db.query(func.sum(Contract.total_cost_usd)).filter(
            Contract.node_id.in_([n.id for n in nodes]),
            Contract.status == 'completed'
        ).scalar() or Decimal('0')

        active_contracts = db.query(func.count(Contract.id)).filter(
            Contract.node_id.in_([n.id for n in nodes]),
            Contract.status == 'active'
        ).scalar() or 0

        stats["provider"] = {
            "total_nodes": len(nodes),
            "total_ram_gb": sum(n.total_ram_gb for n in nodes),
            "available_ram_gb": sum(n.available_ram_gb for n in nodes),
            "total_vram_gb": sum(n.total_vram_gb for n in nodes),
            "available_vram_gb": sum(n.available_vram_gb for n in nodes),
            "total_earnings": float(total_earnings),
            "active_contracts": active_contracts
        }

    # Client stats
    client = db.query(Client).filter(Client.user_id == current_user.id).first()
    if client:
        total_spending = db.query(func.sum(Contract.total_cost_usd)).filter(
            Contract.client_id == client.id
        ).scalar() or Decimal('0')

        active_contracts = db.query(func.count(Contract.id)).filter(
            Contract.client_id == client.id,
            Contract.status == 'active'
        ).scalar() or 0

        stats["client"] = {
            "org_name": client.org_name,
            "total_spending": float(total_spending),
            "current_spend": float(client.current_spend_usd),
            "budget_monthly": float(client.budget_monthly_usd) if client.budget_monthly_usd else None,
            "active_contracts": active_contracts
        }

    # Market overview
    market_supply = await get_market_supply(db=db)
    stats["market"] = {
        "total_nodes": market_supply.total_nodes,
        "total_ram_gb": market_supply.total_ram_gb,
        "available_ram_gb": market_supply.available_ram_gb,
        "utilization_rate": float(market_supply.utilization_rate)
    }

    return stats


@router.get("/node/{node_id}/metrics", response_model=list)
async def get_node_metrics_history(
    node_id: UUID,
    hours: int = Query(24, ge=1, le=168),
    current_user: User = Depends(get_current_user_flexible),
    db: Session = Depends(get_db)
):
    """
    Get historical metrics for a node

    Args:
        node_id: Node UUID
        hours: Number of hours of history
        current_user: Authenticated user
        db: Database session

    Returns:
        List of metric snapshots
    """
    # Verify node
    node = db.query(Node).filter(Node.id == node_id).first()
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Node not found"
        )

    # Get metrics
    start_time = datetime.utcnow() - timedelta(hours=hours)

    metrics = db.query(NodeMetric).filter(
        NodeMetric.node_id == node_id,
        NodeMetric.timestamp >= start_time
    ).order_by(
        NodeMetric.timestamp.asc()
    ).all()

    return [
        {
            "timestamp": m.timestamp.isoformat(),
            "available_ram_gb": m.available_ram_gb,
            "available_vram_gb": m.available_vram_gb,
            "cpu_usage_pct": float(m.cpu_usage_pct) if m.cpu_usage_pct else None,
            "gpu_usage_pct": float(m.gpu_usage_pct) if m.gpu_usage_pct else None,
            "temperature_c": m.temperature_c
        }
        for m in metrics
    ]
