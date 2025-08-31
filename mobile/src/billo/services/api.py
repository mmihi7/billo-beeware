import json
import httpx
from typing import Optional, Dict, Any, List
from urllib.parse import urljoin
import logging

class APIService:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.token: Optional[str] = None
        self.client = httpx.AsyncClient()
        self.ws_client = None
        self.logger = logging.getLogger(__name__)
        
    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make an HTTP request to the API"""
        url = urljoin(self.base_url, endpoint)
        headers = kwargs.pop('headers', {})
        
        if self.token:
            headers['Authorization'] = f"Bearer {self.token}"
            
        try:
            response = await self.client.request(
                method,
                url,
                headers=headers,
                **kwargs
            )
            response.raise_for_status()
            return response.json() if response.content else {}
            
        except httpx.HTTPStatusError as e:
            self.logger.error(f"HTTP error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Request failed: {e}")
            raise
    
    # Authentication
    async def login(self, email: str, password: str) -> Dict[str, Any]:
        """Login and get JWT token"""
        data = {
            "username": email,
            "password": password
        }
        response = await self._request("POST", "auth/login", json=data)
        if "access_token" in response:
            self.token = response["access_token"]
        return response
    
    async def register(self, email: str, password: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new user"""
        data = {
            "email": email,
            "password": password,
            **user_data
        }
        return await self._request("POST", "auth/register", json=data)
    
    # Menu
    async def get_menu(self, restaurant_id: str) -> List[Dict[str, Any]]:
        """Get menu for a restaurant"""
        return await self._request("GET", f"restaurants/{restaurant_id}/menu")
    
    # Orders
    async def create_order(self, restaurant_id: str, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a new order"""
        data = {
            "restaurant_id": restaurant_id,
            "items": items
        }
        return await self._request("POST", "orders/", json=data)
    
    async def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """Get status of an order"""
        return await self._request("GET", f"orders/{order_id}")
    
    # WebSocket
    async def connect_websocket(self, order_id: str, on_message, on_error):
        """Connect to WebSocket for real-time updates"""
        try:
            ws_url = self.base_url.replace('http', 'ws') + f"ws/orders/{order_id}"
            async with httpx.AsyncClient() as client:
                async with client.ws_connect(ws_url) as websocket:
                    self.ws_client = websocket
                    async for message in websocket.iter_text():
                        on_message(json.loads(message))
        except Exception as e:
            self.logger.error(f"WebSocket error: {e}")
            on_error(e)
        finally:
            self.ws_client = None
    
    async def close(self):
        """Clean up resources"""
        if self.ws_client:
            await self.ws_client.close()
        await self.client.aclose()

# Singleton instance
api_service: Optional[APIService] = None

def get_api_service() -> APIService:
    """Get the API service instance"""
    global api_service
    if api_service is None:
        # This should come from config
        api_service = APIService("http://localhost:8000/api/v1/")
    return api_service
