from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import desc
from fastapi import HTTPException, status
from app.models.node import Node
from app.models.telemetry import NodeTelemetry
from app.schemas.telemetry import TelemetryCreate


class TelemetryService:
    """Service for handling node telemetry data."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_telemetry(
        self,
        node_id: int,
        data: TelemetryCreate
    ) -> NodeTelemetry:
        """
        Create a new telemetry entry and update node's VRAM estimate.
        
        Args:
            node_id: ID of the node
            data: Telemetry data
        
        Returns:
            Created telemetry record
        """
        # Verify node exists
        node = self.db.query(Node).filter(Node.id == node_id).first()
        if not node:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Node not found"
            )
        
        # Create telemetry record
        telemetry = NodeTelemetry(
            node_id=node_id,
            vram_gb_free=data.vram_gb_free,
            utilization_percent=data.utilization_percent,
            temperature_c=data.temperature_c
        )
        self.db.add(telemetry)
        
        # Update node's VRAM free estimate
        node.vram_gb_free_estimate = data.vram_gb_free
        
        self.db.commit()
        self.db.refresh(telemetry)
        return telemetry
    
    def get_node_telemetry(
        self,
        node_id: int,
        limit: int = 100
    ) -> List[NodeTelemetry]:
        """
        Get recent telemetry for a node.
        
        Args:
            node_id: ID of the node
            limit: Maximum number of records to return
        
        Returns:
            List of telemetry records, newest first
        """
        return self.db.query(NodeTelemetry).filter(
            NodeTelemetry.node_id == node_id
        ).order_by(
            desc(NodeTelemetry.collected_at)
        ).limit(limit).all()
