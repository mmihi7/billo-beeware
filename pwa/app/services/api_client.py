import json
from typing import Any, Dict, Optional
from httpx import AsyncClient, RequestError
from ..services.config import settings
from shared.utils.api_client import APIClient as BaseAPIClient
from shared.models.base import ResponseModel
import logging

logger = logging.getLogger(__name__)

class PWAApiClient(BaseAPIClient):
    """PWA-specific API client with browser storage integration"""
    
    def __init__(self):
        base_url = f"{settings.API_BASE_URL}/api/{settings.API_VERSION}"
        super().__init__(base_url=base_url)
        self._token = None
        self._load_token()
    
    def _load_token(self):
        """Load token from local storage"""
        if not hasattr(self, '_local_storage'):
            # This will be set by the service provider
            return
        try:
            self._token = self._local_storage.get(settings.TOKEN_KEY)
            if self._token:
                self.client.headers.update({"Authorization": f"Bearer {self._token}"})
        except Exception as e:
            logger.error(f"Error loading token: {e}")
    
    def set_local_storage(self, storage):
        """Set the local storage implementation"""
        self._local_storage = storage
        self._load_token()
    
    def set_token(self, token: Optional[str]):
        """Set the authentication token"""
        self._token = token
        if token:
            self.client.headers.update({"Authorization": f"Bearer {token}"})
            if hasattr(self, '_local_storage'):
                self._local_storage.set(settings.TOKEN_KEY, token)
        else:
            self.client.headers.pop("Authorization", None)
            if hasattr(self, '_local_storage'):
                self._local_storage.remove(settings.TOKEN_KEY)
    
    async def request(self, method: str, endpoint: str, **kwargs) -> ResponseModel:
        """Make an HTTP request with error handling"""
        try:
            response = await super().request(method, endpoint, **kwargs)
            
            # Handle token refresh if needed (401 Unauthorized)
            if response.error and response.error.get("code") == 401:
                # TODO: Implement token refresh logic
                pass
                
            return response
            
        except RequestError as e:
            logger.error(f"Request failed: {e}")
            return ResponseModel(
                success=False,
                message="Network error occurred",
                error={"code": 0, "detail": str(e)}
            )
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return ResponseModel(
                success=False,
                message="An unexpected error occurred",
                error={"code": 500, "detail": str(e)}
            )

# Singleton instance
api_client = PWAApiClient()

def get_api_client() -> PWAApiClient:
    """Get the PWA API client instance"""
    return api_client
