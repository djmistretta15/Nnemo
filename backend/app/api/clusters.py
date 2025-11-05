"""
Cluster visualization API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from uuid import UUID
from decimal import Decimal

from app.database import get_db
from app.models import Node, Cluster
from app.api.schemas import ClusterResponse, ClustersListResponse

router = APIRouter(prefix="/api/clusters", tags=["Clusters"])


async def update_cluster_stats(db: Session):
    """
    Update cluster statistics from current node data
    This would typically run as a background job
    """
    # Get all regions
    regions = db.query(Node.region).distinct().all()

    for (region,) in regions:
        # Get nodes in this region
        nodes = db.query(Node).filter(
            Node.region == region,
            Node.status == 'active'
        ).all()

        if not nodes:
            continue

        # Calculate aggregate stats
        total_nodes = len(nodes)
        datacenter_nodes = sum(1 for n in nodes if n.node_type == 'datacenter')
        edge_nodes = sum(1 for n in nodes if n.node_type == 'edge_cluster')
        mist_nodes = sum(1 for n in nodes if n.node_type == 'mist_node')

        total_ram_gb = sum(n.total_ram_gb for n in nodes)
        available_ram_gb = sum(n.available_ram_gb for n in nodes)
        total_vram_gb = sum(n.total_vram_gb for n in nodes)
        available_vram_gb = sum(n.available_vram_gb for n in nodes)

        # Calculate average price
        avg_price = sum(n.price_per_gb_sec for n in nodes) / len(nodes)

        # Calculate center point (average lat/lng)
        nodes_with_coords = [n for n in nodes if n.latitude and n.longitude]
        if nodes_with_coords:
            center_lat = sum(float(n.latitude) for n in nodes_with_coords) / len(nodes_with_coords)
            center_lng = sum(float(n.longitude) for n in nodes_with_coords) / len(nodes_with_coords)
        else:
            center_lat = None
            center_lng = None

        # Update or create cluster
        cluster = db.query(Cluster).filter(Cluster.region == region).first()

        if cluster:
            cluster.total_nodes = total_nodes
            cluster.datacenter_nodes = datacenter_nodes
            cluster.edge_nodes = edge_nodes
            cluster.mist_nodes = mist_nodes
            cluster.total_ram_gb = total_ram_gb
            cluster.available_ram_gb = available_ram_gb
            cluster.total_vram_gb = total_vram_gb
            cluster.available_vram_gb = available_vram_gb
            cluster.avg_price_per_gb_sec = avg_price
            cluster.center_latitude = Decimal(str(center_lat)) if center_lat else None
            cluster.center_longitude = Decimal(str(center_lng)) if center_lng else None
        else:
            cluster = Cluster(
                region=region,
                total_nodes=total_nodes,
                datacenter_nodes=datacenter_nodes,
                edge_nodes=edge_nodes,
                mist_nodes=mist_nodes,
                total_ram_gb=total_ram_gb,
                available_ram_gb=available_ram_gb,
                total_vram_gb=total_vram_gb,
                available_vram_gb=available_vram_gb,
                avg_price_per_gb_sec=avg_price,
                center_latitude=Decimal(str(center_lat)) if center_lat else None,
                center_longitude=Decimal(str(center_lng)) if center_lng else None
            )
            db.add(cluster)

    db.commit()


@router.get("", response_model=ClustersListResponse)
async def list_clusters(db: Session = Depends(get_db)):
    """
    Get all geographic clusters with statistics

    Args:
        db: Database session

    Returns:
        List of clusters
    """
    # Update cluster stats
    await update_cluster_stats(db)

    # Get all clusters
    clusters = db.query(Cluster).all()

    cluster_responses = []
    for cluster in clusters:
        cluster_responses.append(
            ClusterResponse(
                region=cluster.region,
                center={
                    "lat": cluster.center_latitude if cluster.center_latitude else Decimal('0'),
                    "lng": cluster.center_longitude if cluster.center_longitude else Decimal('0')
                },
                total_nodes=cluster.total_nodes,
                node_composition={
                    "datacenter": cluster.datacenter_nodes,
                    "edge_cluster": cluster.edge_nodes,
                    "mist_node": cluster.mist_nodes
                },
                total_ram_gb=cluster.total_ram_gb,
                available_ram_gb=cluster.available_ram_gb,
                total_vram_gb=cluster.total_vram_gb,
                available_vram_gb=cluster.available_vram_gb,
                avg_price_per_gb_sec=cluster.avg_price_per_gb_sec
            )
        )

    return ClustersListResponse(clusters=cluster_responses)


@router.get("/{region}", response_model=ClusterResponse)
async def get_cluster(region: str, db: Session = Depends(get_db)):
    """
    Get specific cluster details

    Args:
        region: Region identifier
        db: Database session

    Returns:
        Cluster details
    """
    # Update stats
    await update_cluster_stats(db)

    cluster = db.query(Cluster).filter(Cluster.region == region).first()

    if not cluster:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cluster not found for region: {region}"
        )

    return ClusterResponse(
        region=cluster.region,
        center={
            "lat": cluster.center_latitude if cluster.center_latitude else Decimal('0'),
            "lng": cluster.center_longitude if cluster.center_longitude else Decimal('0')
        },
        total_nodes=cluster.total_nodes,
        node_composition={
            "datacenter": cluster.datacenter_nodes,
            "edge_cluster": cluster.edge_nodes,
            "mist_node": cluster.mist_nodes
        },
        total_ram_gb=cluster.total_ram_gb,
        available_ram_gb=cluster.available_ram_gb,
        total_vram_gb=cluster.total_vram_gb,
        available_vram_gb=cluster.available_vram_gb,
        avg_price_per_gb_sec=cluster.avg_price_per_gb_sec
    )


@router.get("/{region}/nodes", response_model=list)
async def get_cluster_nodes(region: str, db: Session = Depends(get_db)):
    """
    Get all nodes in a specific cluster

    Args:
        region: Region identifier
        db: Database session

    Returns:
        List of nodes in cluster
    """
    nodes = db.query(Node).filter(
        Node.region == region,
        Node.status == 'active'
    ).all()

    return [
        {
            "id": str(node.id),
            "name": node.name,
            "node_type": node.node_type,
            "available_ram_gb": node.available_ram_gb,
            "available_vram_gb": node.available_vram_gb,
            "price_per_gb_sec": float(node.price_per_gb_sec),
            "uptime_score": float(node.uptime_score),
            "latitude": float(node.latitude) if node.latitude else None,
            "longitude": float(node.longitude) if node.longitude else None
        }
        for node in nodes
    ]


@router.get("/{region}/stats", response_model=dict)
async def get_cluster_detailed_stats(region: str, db: Session = Depends(get_db)):
    """
    Get detailed cluster statistics

    Args:
        region: Region identifier
        db: Database session

    Returns:
        Detailed statistics
    """
    # Get cluster
    cluster = db.query(Cluster).filter(Cluster.region == region).first()

    if not cluster:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cluster not found for region: {region}"
        )

    # Get nodes
    nodes = db.query(Node).filter(
        Node.region == region,
        Node.status == 'active'
    ).all()

    # Calculate utilization
    total_capacity = cluster.total_ram_gb + cluster.total_vram_gb
    available_capacity = cluster.available_ram_gb + cluster.available_vram_gb
    utilized_capacity = total_capacity - available_capacity

    utilization_rate = (
        (utilized_capacity / total_capacity * 100)
        if total_capacity > 0 else 0
    )

    # Network effect score (more nodes = higher score)
    network_effect_score = min(100, cluster.total_nodes * 2)  # Cap at 100

    return {
        "region": cluster.region,
        "total_nodes": cluster.total_nodes,
        "node_types": {
            "datacenter": cluster.datacenter_nodes,
            "edge_cluster": cluster.edge_nodes,
            "mist_node": cluster.mist_nodes
        },
        "capacity": {
            "total_ram_gb": cluster.total_ram_gb,
            "available_ram_gb": cluster.available_ram_gb,
            "total_vram_gb": cluster.total_vram_gb,
            "available_vram_gb": cluster.available_vram_gb,
            "utilization_rate": round(utilization_rate, 2)
        },
        "pricing": {
            "avg_price_per_gb_sec": float(cluster.avg_price_per_gb_sec),
            "min_price": float(min(n.price_per_gb_sec for n in nodes)) if nodes else 0,
            "max_price": float(max(n.price_per_gb_sec for n in nodes)) if nodes else 0
        },
        "performance": {
            "avg_uptime_score": round(sum(n.uptime_score for n in nodes) / len(nodes), 2) if nodes else 0,
            "avg_latency_ms": round(sum(n.base_latency_ms for n in nodes) / len(nodes), 2) if nodes else 0,
            "network_effect_score": network_effect_score
        },
        "location": {
            "center_lat": float(cluster.center_latitude) if cluster.center_latitude else None,
            "center_lng": float(cluster.center_longitude) if cluster.center_longitude else None
        }
    }
