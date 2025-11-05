"""
Matching algorithm for pairing clients with optimal nodes

Scoring system (max ~300 points):
- Proximity: 0-100 points (3x weight if prefer_local)
- Price: 0-50 points
- Reliability: 0-50 points (uptime_score * 0.5)
- Capacity: 0-30 points (overcapacity bonus)
- Node type bonus: +20 for mist_nodes (community preference)
"""

from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.models import Node, Client
from decimal import Decimal
import math
import uuid


def calculate_distance(
    lat1: float,
    lng1: float,
    lat2: float,
    lng2: float
) -> float:
    """
    Calculate distance between two points in km using Haversine formula

    Args:
        lat1: Latitude of point 1
        lng1: Longitude of point 1
        lat2: Latitude of point 2
        lng2: Longitude of point 2

    Returns:
        Distance in kilometers
    """
    R = 6371  # Earth radius in km

    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)

    a = (
        math.sin(dlat / 2) ** 2 +
        math.cos(math.radians(lat1)) *
        math.cos(math.radians(lat2)) *
        math.sin(dlng / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def match_nodes(
    db: Session,
    client: Client,
    requirements: Dict
) -> List[Dict]:
    """
    Match client requirements to best nodes

    Args:
        db: Database session
        client: Client object making the request
        requirements: Dictionary with ram_gb, vram_gb, duration_sec, etc.

    Returns:
        List of match dictionaries sorted by score
    """
    ram_needed = requirements['ram_gb']
    vram_needed = requirements['vram_gb']
    max_price = requirements['max_price_per_gb_sec']
    prefer_local = requirements.get('prefer_local', True)
    max_distance = requirements.get('max_distance_km', 10000)
    min_uptime = requirements.get('min_uptime_score', 0)

    # Query available nodes
    available_nodes = db.query(Node).filter(
        Node.available_ram_gb >= ram_needed,
        Node.available_vram_gb >= vram_needed,
        Node.price_per_gb_sec <= max_price,
        Node.status == 'active',
        Node.uptime_score >= min_uptime
    ).all()

    matches = []

    for node in available_nodes:
        score = Decimal('0')
        distance = None

        # 1. PROXIMITY SCORE (most important if prefer_local)
        if (
            client.latitude and client.longitude and
            node.latitude and node.longitude
        ):
            distance = calculate_distance(
                float(client.latitude),
                float(client.longitude),
                float(node.latitude),
                float(node.longitude)
            )

            # Skip nodes outside max distance
            if distance > max_distance:
                continue

            # Score: 100 at 0km, decreasing to 0 at 1000km
            proximity_score = Decimal(str(max(0, 100 - (distance / 10))))

            # Apply 3x weight if prefer_local
            if prefer_local:
                score += proximity_score * Decimal('3')
            else:
                score += proximity_score
        else:
            proximity_score = Decimal('0')

        # 2. PRICE SCORE (lower price = higher score)
        price_ratio = Decimal('1') - (node.price_per_gb_sec / max_price)
        price_score = price_ratio * Decimal('50')
        score += price_score

        # 3. RELIABILITY SCORE
        reliability_score = node.uptime_score * Decimal('0.5')  # Max 50 points
        score += reliability_score

        # 4. CAPACITY SCORE (overcapacity = better failover)
        total_needed = ram_needed + vram_needed
        total_available = node.available_ram_gb + node.available_vram_gb
        capacity_ratio = Decimal(str(total_available / total_needed))
        capacity_score = min(Decimal('30'), capacity_ratio * Decimal('10'))  # Max 30
        score += capacity_score

        # 5. NODE TYPE BONUS (encourage mist node usage)
        node_type_bonus = Decimal('0')
        if node.node_type == 'mist_node':
            node_type_bonus = Decimal('20')  # Community preference bonus
            score += node_type_bonus

        # Calculate estimated cost
        duration_sec = requirements.get('duration_sec', 3600)
        total_gb = ram_needed + vram_needed
        estimated_cost = (
            Decimal(str(total_gb)) *
            Decimal(str(duration_sec)) *
            node.price_per_gb_sec
        )

        matches.append({
            'node_id': str(node.id),
            'node_name': node.name,
            'node_type': node.node_type,
            'region': node.region,
            'match_score': float(round(score, 2)),
            'distance_km': round(distance, 2) if distance else None,
            'estimated_cost': float(round(estimated_cost, 4)),
            'estimated_latency_ms': float(node.base_latency_ms),

            # Score breakdown (for transparency)
            'score_breakdown': {
                'proximity': float(round(proximity_score, 2)),
                'price': float(round(price_score, 2)),
                'reliability': float(round(reliability_score, 2)),
                'capacity': float(round(capacity_score, 2)),
                'node_type_bonus': float(node_type_bonus)
            }
        })

    # Sort by match score (highest first)
    matches.sort(key=lambda x: x['match_score'], reverse=True)

    return matches


def find_best_match(
    db: Session,
    client: Client,
    requirements: Dict
) -> Optional[Dict]:
    """
    Find single best match for a client request

    Args:
        db: Database session
        client: Client object
        requirements: Memory requirements

    Returns:
        Best match dictionary or None if no matches
    """
    matches = match_nodes(db, client, requirements)
    return matches[0] if matches else None
