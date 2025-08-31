from typing import List, Optional, Dict, Any
from ..models.commerce import OrderCreate, OrderUpdate, OrderResponse, OrderStatus
from ..utils.api_client import get_api_client
import logging

logger = logging.getLogger(__name__)

class OrderService:
    def __init__(self):
        self.api = get_api_client()
    
    async def create_order(self, order_data: OrderCreate) -> OrderResponse:
        """Create a new order"""
        try:
            response = await self.api.post(
                "orders/",
                json=order_data.dict(),
                response_model=OrderResponse
            )
            if not response.success:
                logger.error(f"Failed to create order: {response.error}")
            return response
        except Exception as e:
            logger.error(f"Error creating order: {str(e)}")
            raise
    
    async def get_order(self, order_id: str) -> Optional[OrderResponse]:
        """Get order by ID"""
        try:
            response = await self.api.get(
                f"orders/{order_id}",
                response_model=OrderResponse
            )
            if not response.success:
                logger.warning(f"Order not found: {order_id}")
                return None
            return response.data
        except Exception as e:
            logger.error(f"Error fetching order: {str(e)}")
            raise
    
    async def update_order_status(
        self, 
        order_id: str, 
        status: OrderStatus,
        notes: Optional[str] = None
    ) -> Optional[OrderResponse]:
        """Update order status"""
        try:
            update_data = {"status": status}
            if notes is not None:
                update_data["notes"] = notes
                
            response = await self.api.patch(
                f"orders/{order_id}",
                json=update_data,
                response_model=OrderResponse
            )
            
            if not response.success:
                logger.error(f"Failed to update order: {response.error}")
                return None
                
            return response.data
        except Exception as e:
            logger.error(f"Error updating order: {str(e)}")
            raise
    
    async def list_orders(
        self,
        restaurant_id: Optional[str] = None,
        status: Optional[OrderStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[OrderResponse]:
        """List orders with optional filters"""
        try:
            params = {"limit": limit, "offset": offset}
            if restaurant_id:
                params["restaurant_id"] = restaurant_id
            if status:
                params["status"] = status
                
            response = await self.api.get(
                "orders/",
                params=params,
                response_model=List[OrderResponse]
            )
            
            if not response.success:
                logger.error(f"Failed to list orders: {response.error}")
                return []
                
            return response.data or []
        except Exception as e:
            logger.error(f"Error listing orders: {str(e)}")
            raise
    
    async def cancel_order(
        self, 
        order_id: str,
        reason: Optional[str] = None
    ) -> bool:
        """Cancel an order"""
        try:
            response = await self.api.delete(
                f"orders/{order_id}",
                json={"reason": reason} if reason else None
            )
            
            if not response.success:
                logger.error(f"Failed to cancel order: {response.error}")
                return False
                
            return True
        except Exception as e:
            logger.error(f"Error canceling order: {str(e)}")
            raise

# Singleton instance
order_service: Optional[OrderService] = None

def get_order_service() -> OrderService:
    """Get or create the order service instance"""
    global order_service
    if order_service is None:
        order_service = OrderService()
    return order_service
