import httpx
import json
from typing import Any, Dict, Optional, TypeVar, Type
from ..models.base import ResponseModel, T
from ..config import settings
import logging

logger = logging.getLogger(__name__)

class APIClient:
    def __init__(self, base_url: str, token: Optional[str] = None):
        self.base_url = base_url
        self.token = token
        self.client = httpx.AsyncClient()
    
    async def request(
        self,
        method: str,
        endpoint: str,
        response_model: Type[T] = None,
        **kwargs
    ) -> ResponseModel[T]:
        """Make an HTTP request to the API."""
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        headers = kwargs.pop('headers', {})
        
        if self.token:
            headers['Authorization'] = f"Bearer {self.token}"
        
        try:
            response = await self.client.request(
                method=method,
                url=url,
                headers=headers,
                **kwargs
            )
            response.raise_for_status()
            
            # Parse response
            response_data = response.json()
            
            # If a response model is provided, validate the data
            if response_model:
                if 'data' in response_data:
                    response_data['data'] = response_model(**response_data['data'])
                elif isinstance(response_data, dict):
                    response_data = response_model(**response_data)
            
            return ResponseModel(**response_data)
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e}")
            return ResponseModel(
                success=False,
                message=str(e),
                error={"code": e.response.status_code, "detail": str(e)}
            )
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return ResponseModel(
                success=False,
                message="Invalid JSON response",
                error={"code": 500, "detail": str(e)}
            )
        except Exception as e:
            logger.error(f"Request failed: {e}")
            return ResponseModel(
                success=False,
                message="An unexpected error occurred",
                error={"code": 500, "detail": str(e)}
            )
    
    async def get(self, endpoint: str, **kwargs) -> ResponseModel[T]:
        return await self.request("GET", endpoint, **kwargs)
    
    async def post(self, endpoint: str, **kwargs) -> ResponseModel[T]:
        return await self.request("POST", endpoint, **kwargs)
    
    async def put(self, endpoint: str, **kwargs) -> ResponseModel[T]:
        return await self.request("PUT", endpoint, **kwargs)
    
    async def delete(self, endpoint: str, **kwargs) -> ResponseModel[T]:
        return await self.request("DELETE", endpoint, **kwargs)
    
    async def close(self):
        await self.client.aclose()

# Singleton instance
api_client: Optional[APIClient] = None

def get_api_client() -> APIClient:
    """Get or create the API client instance."""
    global api_client
    if api_client is None:
        from ..config import settings
        api_client = APIClient(settings.API_V1_STR)
    return api_client
