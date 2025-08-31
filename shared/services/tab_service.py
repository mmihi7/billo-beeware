from typing import List, Optional, Dict, Any
from ..models.commerce import TabCreate, TabUpdate, TabResponse, TabStatus, OrderBase
from ..utils.api_client import get_api_client
import logging

logger = logging.getLogger(__name__)

class TabService:
    def __init__(self):
        self.api = get_api_client()
    
    async def create_tab(self, tab_data: TabCreate) -> Optional[TabResponse]:
        """Create a new customer tab"""
        try:
            response = await self.api.post(
                "tabs/",
                json=tab_data.dict(),
                response_model=TabResponse
            )
            
            if not response.success:
                logger.error(f"Failed to create tab: {response.error}")
                return None
                
            return response.data
        except Exception as e:
            logger.error(f"Error creating tab: {str(e)}")
            raise
    
    async def get_tab(self, tab_id: str) -> Optional[TabResponse]:
        """Get tab by ID with related orders and payments"""
        try:
            response = await self.api.get(
                f"tabs/{tab_id}",
                response_model=TabResponse
            )
            
            if not response.success:
                logger.warning(f"Tab not found: {tab_id}")
                return None
                
            return response.data
        except Exception as e:
            logger.error(f"Error fetching tab: {str(e)}")
            raise
    
    async def update_tab(
        self,
        tab_id: str,
        status: Optional[TabStatus] = None,
        notes: Optional[str] = None
    ) -> Optional[TabResponse]:
        """Update tab information"""
        try:
            update_data = {}
            if status is not None:
                update_data["status"] = status
            if notes is not None:
                update_data["notes"] = notes
                
            if not update_data:
                return await self.get_tab(tab_id)
                
            response = await self.api.patch(
                f"tabs/{tab_id}",
                json=update_data,
                response_model=TabResponse
            )
            
            if not response.success:
                logger.error(f"Failed to update tab: {response.error}")
                return None
                
            return response.data
        except Exception as e:
            logger.error(f"Error updating tab: {str(e)}")
            raise
    
    async def close_tab(self, tab_id: str) -> bool:
        """Close a customer tab"""
        try:
            response = await self.api.patch(
                f"tabs/{tab_id}/close",
                response_model=TabResponse
            )
            
            if not response.success:
                logger.error(f"Failed to close tab: {response.error}")
                return False
                
            return True
        except Exception as e:
            logger.error(f"Error closing tab: {str(e)}")
            raise
    
    async def add_order_to_tab(self, tab_id: str, order: OrderBase) -> bool:
        """Add an order to a tab"""
        try:
            response = await self.api.post(
                f"tabs/{tab_id}/orders",
                json={"order_id": order.id}
            )
            
            if not response.success:
                logger.error(f"Failed to add order to tab: {response.error}")
                return False
                
            return True
        except Exception as e:
            logger.error(f"Error adding order to tab: {str(e)}")
            raise
    
    async def list_tabs(
        self,
        restaurant_id: Optional[str] = None,
        customer_id: Optional[str] = None,
        status: Optional[TabStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[TabResponse]:
        """List tabs with optional filters"""
        try:
            params = {"limit": limit, "offset": offset}
            if restaurant_id:
                params["restaurant_id"] = restaurant_id
            if customer_id:
                params["customer_id"] = customer_id
            if status:
                params["status"] = status
                
            response = await self.api.get(
                "tabs/",
                params=params,
                response_model=List[TabResponse]
            )
            
            if not response.success:
                logger.error(f"Failed to list tabs: {response.error}")
                return []
                
            return response.data or []
        except Exception as e:
            logger.error(f"Error listing tabs: {str(e)}")
            raise

# Singleton instance
tab_service: Optional[TabService] = None

def get_tab_service() -> TabService:
    """Get or create the tab service instance"""
    global tab_service
    if tab_service is None:
        tab_service = TabService()
    return tab_service
