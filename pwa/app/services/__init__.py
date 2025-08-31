"""PWA Services Initialization"""
import json
from typing import Any, Optional, Callable
from .config import settings
from .api_client import get_api_client, PWAApiClient
from .auth import get_auth_service, PWAAuthService
from shared.services import (
    get_order_service,
    get_payment_service,
    get_tab_service
)

class LocalStorage:
    """Browser localStorage wrapper"""
    def __init__(self, storage):
        self.storage = storage
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get item from storage"""
        try:
            value = self.storage.getItem(key)
            return json.loads(value) if value else default
        except Exception:
            return default
    
    def set(self, key: str, value: Any) -> None:
        """Set item in storage"""
        try:
            self.storage.setItem(key, json.dumps(value))
        except Exception as e:
            print(f"Error setting {key} in storage: {e}")
    
    def remove(self, key: str) -> None:
        """Remove item from storage"""
        try:
            self.storage.removeItem(key)
        except Exception as e:
            print(f"Error removing {key} from storage: {e}")

class ServiceProvider:
    """Service provider for PWA application"""
    _instance = None
    
    def __init__(self, storage=None):
        if ServiceProvider._instance is not None:
            raise Exception("ServiceProvider is a singleton!")
        
        self._initialized = False
        self._storage = None
        self._api_client = None
        self._auth_service = None
        
        if storage:
            self.initialize(storage)
    
    @classmethod
    def get_instance(cls, storage=None):
        """Get or create the service provider instance"""
        if cls._instance is None:
            cls._instance = cls(storage)
        elif storage and not cls._instance._initialized:
            cls._instance.initialize(storage)
        return cls._instance
    
    def initialize(self, storage):
        """Initialize all services with the given storage"""
        if self._initialized:
            return
            
        self._storage = LocalStorage(storage)
        
        # Initialize API client
        self._api_client = get_api_client()
        self._api_client.set_local_storage(self._storage)
        
        # Initialize auth service
        self._auth_service = get_auth_service()
        self._auth_service.set_local_storage(self._storage)
        
        # Initialize other services
        self._order_service = get_order_service()
        self._payment_service = get_payment_service()
        self._tab_service = get_tab_service()
        
        self._initialized = True
    
    @property
    def api(self) -> PWAApiClient:
        """Get the API client"""
        if not self._initialized:
            raise RuntimeError("ServiceProvider not initialized")
        return self._api_client
    
    @property
    def auth(self) -> PWAAuthService:
        """Get the auth service"""
        if not self._initialized:
            raise RuntimeError("ServiceProvider not initialized")
        return self._auth_service
    
    @property
    def orders(self):
        """Get the order service"""
        if not self._initialized:
            raise RuntimeError("ServiceProvider not initialized")
        return self._order_service
    
    @property
    def payments(self):
        """Get the payment service"""
        if not self._initialized:
            raise RuntimeError("ServiceProvider not initialized")
        return self._payment_service
    
    @property
    def tabs(self):
        """Get the tab service"""
        if not self._initialized:
            raise RuntimeError("ServiceProvider not initialized")
        return self._tab_service

# Export services
def get_services(storage=None) -> ServiceProvider:
    """Get the service provider instance"""
    return ServiceProvider.get_instance(storage)
