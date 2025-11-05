"""
WebSocket API endpoints for real-time updates
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.auth import decode_token
from app.websocket import manager
import json

router = APIRouter()


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: str,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for real-time updates

    Query params:
        token: JWT token for authentication

    Usage:
        ws://localhost:8000/ws/{user_id}?token=YOUR_JWT_TOKEN
    """
    # Verify token
    payload = decode_token(token)
    if not payload or payload.get("sub") != user_id:
        await websocket.close(code=1008, reason="Unauthorized")
        return

    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        await websocket.close(code=1008, reason="User not found")
        return

    # Connect
    await manager.connect(websocket, user_id)

    try:
        while True:
            # Receive messages from client
            data = await websocket.receive_text()
            message = json.loads(data)

            # Handle different message types
            msg_type = message.get("type")

            if msg_type == "subscribe":
                # Subscribe to topic
                topic = message.get("topic")
                if topic:
                    await manager.subscribe(user_id, topic)

            elif msg_type == "unsubscribe":
                # Unsubscribe from topic
                topic = message.get("topic")
                if topic:
                    await manager.unsubscribe(user_id, topic)

            elif msg_type == "ping":
                # Respond to ping
                await manager.send_personal_message(
                    user_id,
                    {"type": "pong", "timestamp": message.get("timestamp")}
                )

    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
        manager.disconnect(websocket, user_id)
