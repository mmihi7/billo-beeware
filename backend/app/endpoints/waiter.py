from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel
from app.core.jwt import get_current_user
import json

router = APIRouter(prefix="/waiter", tags=["waiter"])

class OrderStatusUpdate(BaseModel):
    status: str
    notes: Optional[str] = None

class WaiterNotification(BaseModel):
    id: str
    type: str  # 'new_order', 'order_ready', 'payment_request', 'assistance'
    message: str
    order_id: Optional[str] = None
    table_number: Optional[int] = None
    created_at: datetime
    is_read: bool = False

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, waiter_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[waiter_id] = websocket

    def disconnect(self, waiter_id: str):
        if waiter_id in self.active_connections:
            del self.active_connections[waiter_id]

    async def send_personal_message(self, message: str, waiter_id: str):
        if waiter_id in self.active_connections:
            await self.active_connections[waiter_id].send_text(message)

manager = ConnectionManager()

@router.websocket("/ws/{waiter_id}")
async def websocket_endpoint(websocket: WebSocket, waiter_id: str):
    await manager.connect(waiter_id, websocket)
    try:
        while True:
            # Keep the connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(waiter_id)

@router.get("/orders", response_model=List[dict])
async def get_waiter_orders(
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Get all orders assigned to the current waiter
    """
    if current_user["role"] not in ["waiter", "restaurant_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only waiters and admins can access this endpoint"
        )
    
    # TODO: Implement order retrieval from Supabase
    # Filter by status if provided
    return []

@router.patch("/orders/{order_id}", response_model=dict)
async def update_order_status(
    order_id: str,
    status_update: OrderStatusUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update order status (e.g., mark as ready, delivered)
    """
    # TODO: Implement order status update in Supabase
    # This is a placeholder implementation
    return {
        "id": order_id,
        "status": status_update.status,
        "updated_at": datetime.utcnow()
    }

@router.get("/notifications", response_model=List[WaiterNotification])
async def get_waiter_notifications(
    unread_only: bool = True,
    current_user: dict = Depends(get_current_user)
):
    """
    Get notifications for the current waiter
    """
    # TODO: Implement notification retrieval from Supabase
    # Filter by unread if unread_only is True
    return []

@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Mark a notification as read
    """
    # TODO: Implement notification update in Supabase
    return {"status": "success"}

# Helper function to send real-time notifications
async def send_waiter_notification(waiter_id: str, notification: dict):
    """
    Send a real-time notification to a specific waiter
    """
    await manager.send_personal_message(
        json.dumps(notification, default=str),
        waiter_id
    )
