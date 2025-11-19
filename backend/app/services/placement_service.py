from typing import Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException, status
from app.models.node import Node
from app.models.model_profile import ModelProfile
from app.models.placement_request import PlacementRequest, PlacementPriority
from app.models.placement_decision import PlacementDecision


class PlacementService:
    """Service for handling placement logic and VRAM-aware node selection."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_fit_score(
        self,
        node: Node,
        required_vram_gb: float
    ) -> Tuple[float, str]:
        """
        Calculate fit score for a node based on VRAM availability and other metrics.
        
        Score formula:
            score = (vram_gb_free_estimate - required_vram_gb) * 0.5
                    + memory_bandwidth_gbps * 0.3
                    - network_latency_ms_estimate * 0.2
        
        Returns:
            Tuple of (score, reason_text)
        """
        # Base score from available VRAM headroom
        vram_headroom = node.vram_gb_free_estimate - required_vram_gb
        vram_score = vram_headroom * 0.5
        
        # Bonus for high memory bandwidth
        bandwidth_score = (node.memory_bandwidth_gbps or 0) * 0.3
        
        # Penalty for high latency
        latency_penalty = (node.network_latency_ms_estimate or 0) * 0.2
        
        total_score = vram_score + bandwidth_score - latency_penalty
        
        # Normalize to 0-100 range (approximate)
        normalized_score = max(0, min(100, total_score))
        
        reason = (
            f"Node '{node.name}' selected with {vram_headroom:.1f}GB VRAM headroom. "
            f"Memory bandwidth: {node.memory_bandwidth_gbps or 0:.1f} GB/s, "
            f"Network latency: {node.network_latency_ms_estimate or 0:.1f}ms. "
            f"Total fit score: {normalized_score:.1f}/100"
        )
        
        return normalized_score, reason
    
    def find_best_node(
        self,
        required_vram_gb: float,
        preferred_region: Optional[str] = None,
        organization_id: Optional[int] = None
    ) -> Tuple[Optional[Node], Optional[float], Optional[str]]:
        """
        Find the best node for a placement request.
        
        Args:
            required_vram_gb: Amount of VRAM required
            preferred_region: Optional preferred region
            organization_id: Optional organization filter
        
        Returns:
            Tuple of (best_node, score, reason) or (None, None, None) if no suitable node
        """
        # Build query for candidate nodes
        query = self.db.query(Node).filter(
            and_(
                Node.is_active == True,
                Node.vram_gb_free_estimate >= required_vram_gb
            )
        )
        
        # Filter by region if specified
        if preferred_region:
            query = query.filter(Node.region == preferred_region)
        
        # Filter by organization if specified
        if organization_id:
            query = query.filter(Node.organization_id == organization_id)
        
        candidates = query.all()
        
        if not candidates:
            return None, None, None
        
        # Score all candidates
        best_node = None
        best_score = -float('inf')
        best_reason = None
        
        for node in candidates:
            score, reason = self.calculate_fit_score(node, required_vram_gb)
            if score > best_score:
                best_score = score
                best_node = node
                best_reason = reason
        
        return best_node, best_score, best_reason
    
    def create_placement(
        self,
        user_id: int,
        organization_id: int,
        model_name: str,
        required_vram_gb: Optional[float] = None,
        preferred_region: Optional[str] = None,
        priority: PlacementPriority = PlacementPriority.normal
    ) -> PlacementDecision:
        """
        Create a placement request and decision.
        
        Args:
            user_id: User making the request
            organization_id: User's organization
            model_name: Name of the model to place
            required_vram_gb: Optional explicit VRAM requirement
            preferred_region: Optional region preference
            priority: Request priority
        
        Returns:
            PlacementDecision with chosen node
        
        Raises:
            HTTPException if no suitable node found or model profile doesn't exist
        """
        # If VRAM not specified, try to infer from ModelProfile
        if required_vram_gb is None:
            profile = self.db.query(ModelProfile).filter(
                ModelProfile.name == model_name
            ).first()
            
            if not profile:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Model profile '{model_name}' not found and required_vram_gb not specified"
                )
            
            required_vram_gb = profile.suggested_min_vram_gb
        
        # Find best node
        best_node, score, reason = self.find_best_node(
            required_vram_gb=required_vram_gb,
            preferred_region=preferred_region,
            organization_id=organization_id
        )
        
        if not best_node:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"No suitable node found for {required_vram_gb}GB VRAM requirement"
                       + (f" in region '{preferred_region}'" if preferred_region else "")
            )
        
        # Create placement request
        placement_request = PlacementRequest(
            user_id=user_id,
            organization_id=organization_id,
            model_name=model_name,
            required_vram_gb=required_vram_gb,
            preferred_region=preferred_region,
            priority=priority
        )
        self.db.add(placement_request)
        self.db.flush()  # Get the ID
        
        # Create placement decision
        decision = PlacementDecision(
            placement_request_id=placement_request.id,
            chosen_node_id=best_node.id,
            reason=reason,
            estimated_fit_score=score
        )
        self.db.add(decision)
        self.db.commit()
        self.db.refresh(decision)
        
        return decision
    
    def get_placement_quote(
        self,
        model_name: str,
        required_vram_gb: float,
        preferred_region: Optional[str] = None
    ) -> Tuple[Optional[Node], Optional[float], Optional[str]]:
        """
        Get a placement quote without persisting (for public API).
        
        Returns:
            Tuple of (best_node, score, reason) or (None, None, None)
        """
        return self.find_best_node(
            required_vram_gb=required_vram_gb,
            preferred_region=preferred_region
        )
