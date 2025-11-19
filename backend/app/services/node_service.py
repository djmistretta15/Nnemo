from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.node import Node
from app.schemas.node import NodeCreate, NodeUpdate


class NodeService:
    """Service for node management operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_node(self, organization_id: int, data: NodeCreate) -> Node:
        """Create a new GPU node."""
        node = Node(
            organization_id=organization_id,
            name=data.name,
            provider_name=data.provider_name,
            region=data.region,
            gpu_model=data.gpu_model,
            vram_gb_total=data.vram_gb_total,
            vram_gb_free_estimate=data.vram_gb_total,  # Initially all VRAM is free
            memory_bandwidth_gbps=data.memory_bandwidth_gbps,
            network_latency_ms_estimate=data.network_latency_ms_estimate,
            is_active=True
        )
        self.db.add(node)
        self.db.commit()
        self.db.refresh(node)
        return node
    
    def get_node(self, node_id: int, organization_id: Optional[int] = None) -> Node:
        """Get a specific node by ID."""
        query = self.db.query(Node).filter(Node.id == node_id)
        
        if organization_id is not None:
            query = query.filter(Node.organization_id == organization_id)
        
        node = query.first()
        if not node:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Node not found"
            )
        return node
    
    def list_nodes(
        self,
        organization_id: Optional[int] = None,
        region: Optional[str] = None,
        provider: Optional[str] = None,
        active: Optional[bool] = None
    ) -> List[Node]:
        """List nodes with optional filters."""
        query = self.db.query(Node)
        
        if organization_id is not None:
            query = query.filter(Node.organization_id == organization_id)
        
        if region:
            query = query.filter(Node.region == region)
        
        if provider:
            query = query.filter(Node.provider_name == provider)
        
        if active is not None:
            query = query.filter(Node.is_active == active)
        
        return query.all()
    
    def update_node(
        self,
        node_id: int,
        organization_id: int,
        data: NodeUpdate
    ) -> Node:
        """Update a node."""
        node = self.get_node(node_id, organization_id)
        
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(node, field, value)
        
        self.db.commit()
        self.db.refresh(node)
        return node
    
    def delete_node(self, node_id: int, organization_id: int) -> None:
        """Deactivate a node (soft delete)."""
        node = self.get_node(node_id, organization_id)
        node.is_active = False
        self.db.commit()
