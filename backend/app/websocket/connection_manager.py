"""
WebSocket server for real-time updates
Handles real-time notifications for:
- Contract status changes
- Node availability updates
- Market updates
- Payment notifications
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Set
import json
import asyncio
from datetime import datetime


class ConnectionManager:
    """Manages WebSocket connections and broadcasts"""

    def __init__(self):
        # Active connections by user_id
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Subscriptions by topic (e.g., "contracts", "nodes", "market")
        self.topic_subscriptions: Dict[str, Set[str]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept and register a new WebSocket connection"""
        await websocket.accept()

        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()

        self.active_connections[user_id].add(websocket)

        # Send welcome message
        await self.send_personal_message(
            user_id,
            {
                "type": "connection",
                "status": "connected",
                "timestamp": datetime.utcnow().isoformat(),
                "message": "WebSocket connection established"
            }
        )

    def disconnect(self, websocket: WebSocket, user_id: str):
        """Remove a WebSocket connection"""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)

            # Remove user if no more connections
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

                # Remove from all topic subscriptions
                for topic in self.topic_subscriptions:
                    self.topic_subscriptions[topic].discard(user_id)

    async def send_personal_message(self, user_id: str, message: dict):
        """Send message to specific user (all their connections)"""
        if user_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except:
                    disconnected.append(connection)

            # Clean up disconnected sockets
            for conn in disconnected:
                self.disconnect(conn, user_id)

    async def broadcast(self, message: dict):
        """Broadcast message to all connected users"""
        for user_id in list(self.active_connections.keys()):
            await self.send_personal_message(user_id, message)

    async def subscribe(self, user_id: str, topic: str):
        """Subscribe user to a topic"""
        if topic not in self.topic_subscriptions:
            self.topic_subscriptions[topic] = set()

        self.topic_subscriptions[topic].add(user_id)

        await self.send_personal_message(
            user_id,
            {
                "type": "subscription",
                "topic": topic,
                "status": "subscribed",
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    async def unsubscribe(self, user_id: str, topic: str):
        """Unsubscribe user from a topic"""
        if topic in self.topic_subscriptions:
            self.topic_subscriptions[topic].discard(user_id)

    async def publish_to_topic(self, topic: str, message: dict):
        """Publish message to all subscribers of a topic"""
        if topic in self.topic_subscriptions:
            for user_id in list(self.topic_subscriptions[topic]):
                await self.send_personal_message(user_id, message)

    async def notify_contract_update(self, contract_id: str, status: str, client_id: str, node_owner_id: str):
        """Notify about contract status changes"""
        message = {
            "type": "contract_update",
            "contract_id": contract_id,
            "status": status,
            "timestamp": datetime.utcnow().isoformat()
        }

        # Notify client
        await self.send_personal_message(client_id, message)

        # Notify node owner
        await self.send_personal_message(node_owner_id, message)

    async def notify_node_update(self, node_id: str, available_ram_gb: int, available_vram_gb: int):
        """Notify about node availability changes"""
        message = {
            "type": "node_update",
            "node_id": node_id,
            "available_ram_gb": available_ram_gb,
            "available_vram_gb": available_vram_gb,
            "timestamp": datetime.utcnow().isoformat()
        }

        # Publish to market topic
        await self.publish_to_topic("market", message)

    async def notify_market_update(self, region: str, total_available_gb: int):
        """Notify about market-wide changes"""
        message = {
            "type": "market_update",
            "region": region,
            "total_available_gb": total_available_gb,
            "timestamp": datetime.utcnow().isoformat()
        }

        await self.publish_to_topic("market", message)

    async def notify_payment(self, user_id: str, transaction_id: str, amount: float, status: str):
        """Notify about payment updates"""
        message = {
            "type": "payment_update",
            "transaction_id": transaction_id,
            "amount": amount,
            "status": status,
            "timestamp": datetime.utcnow().isoformat()
        }

        await self.send_personal_message(user_id, message)


# Global connection manager
manager = ConnectionManager()
