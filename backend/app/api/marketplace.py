"""
Marketplace API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID, uuid4
from decimal import Decimal

from app.database import get_db
from app.models import Node, Client, User
from app.auth import get_current_user_flexible
from app.api.schemas import (
    MarketplaceFilter,
    MarketplaceResponse,
    OfferResponse,
    MemoryRequest,
    MatchResponse,
    MatchResult
)
from app.services.matching import match_nodes, calculate_distance

router = APIRouter(prefix="/api/marketplace", tags=["Marketplace"])


@router.get("", response_model=MarketplaceResponse)
async def browse_marketplace(
    filters: MarketplaceFilter = Depends(),
    db: Session = Depends(get_db)
):
    """
    Browse available memory capacity with filters

    Args:
        filters: Marketplace filter parameters
        db: Database session

    Returns:
        List of available offers
    """
    query = db.query(Node).filter(Node.status == 'active')

    # Apply filters
    if filters.node_type:
        query = query.filter(Node.node_type == filters.node_type)

    if filters.region:
        query = query.filter(Node.region == filters.region)

    if filters.min_ram_gb:
        query = query.filter(Node.available_ram_gb >= filters.min_ram_gb)

    if filters.min_vram_gb:
        query = query.filter(Node.available_vram_gb >= filters.min_vram_gb)

    if filters.max_price_per_gb_sec:
        query = query.filter(Node.price_per_gb_sec <= filters.max_price_per_gb_sec)

    if filters.min_uptime_score:
        query = query.filter(Node.uptime_score >= filters.min_uptime_score)

    # Get total count before pagination
    total_count = query.count()

    # Get nodes
    nodes = query.offset(filters.offset).limit(filters.limit).all()

    # Build offers with distance calculation
    offers = []
    for node in nodes:
        distance_km = None
        if (
            filters.client_lat and filters.client_lng and
            node.latitude and node.longitude
        ):
            distance_km = calculate_distance(
                float(filters.client_lat),
                float(filters.client_lng),
                float(node.latitude),
                float(node.longitude)
            )

            # Skip if beyond max distance
            if filters.max_distance_km and distance_km > filters.max_distance_km:
                continue

        offers.append(
            OfferResponse(
                node_id=node.id,
                node_name=node.name,
                node_type=node.node_type,
                region=node.region,
                available_ram_gb=node.available_ram_gb,
                available_vram_gb=node.available_vram_gb,
                price_per_gb_sec=node.price_per_gb_sec,
                uptime_score=node.uptime_score,
                distance_km=round(Decimal(str(distance_km)), 2) if distance_km else None,
                estimated_latency_ms=node.base_latency_ms
            )
        )

    return MarketplaceResponse(
        offers=offers,
        total_count=total_count
    )


@router.post("/request", response_model=MatchResponse)
async def request_memory(
    request_data: MemoryRequest,
    current_user: User = Depends(get_current_user_flexible),
    db: Session = Depends(get_db)
):
    """
    Request memory with intelligent matching

    Args:
        request_data: Memory request parameters
        current_user: Authenticated user
        db: Database session

    Returns:
        List of matched nodes sorted by match score

    Raises:
        HTTPException: If no client profile or no matches found
    """
    # Get or create client profile
    client = db.query(Client).filter(Client.user_id == current_user.id).first()

    if not client:
        # Create default client profile
        client = Client(
            user_id=current_user.id,
            org_name=current_user.organization or current_user.full_name or "Unknown",
            prefer_local=request_data.prefer_local
        )
        db.add(client)
        db.commit()
        db.refresh(client)

    # Convert request to requirements dict
    requirements = {
        'ram_gb': request_data.ram_gb,
        'vram_gb': request_data.vram_gb,
        'duration_sec': request_data.duration_sec,
        'max_price_per_gb_sec': request_data.max_price_per_gb_sec,
        'prefer_local': request_data.prefer_local,
        'max_distance_km': request_data.max_distance_km or 10000,
        'min_uptime_score': request_data.min_uptime_score or 0
    }

    # Run matching algorithm
    matches = match_nodes(db, client, requirements)

    if not matches:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No suitable nodes found for your requirements"
        )

    # Convert to response format
    match_results = [
        MatchResult(
            node_id=UUID(match['node_id']),
            node_name=match['node_name'],
            node_type=match['node_type'],
            match_score=Decimal(str(match['match_score'])),
            estimated_cost=Decimal(str(match['estimated_cost'])),
            distance_km=Decimal(str(match['distance_km'])) if match['distance_km'] else None,
            estimated_latency_ms=Decimal(str(match['estimated_latency_ms'])),
            score_breakdown={
                k: Decimal(str(v)) for k, v in match['score_breakdown'].items()
            }
        )
        for match in matches[:10]  # Return top 10 matches
    ]

    return MatchResponse(
        request_id=uuid4(),
        matches=match_results
    )
