from typing import Any, Dict, Optional
from shared.services.auth_service import AuthService as BaseAuthService
from .api_client import get_api_client
from ..services.config import settings
import logging

logger = logging.getLogger(__name__)

class PWAAuthService(BaseAuthService):
    """PWA-specific authentication service with browser storage integration"""
    
    def __init__(self):
        super().__init__()
        self._local_storage = None
        self._user = None
    
    def set_local_storage(self, storage):
        """Set the local storage implementation"""
        self._local_storage = storage
        self._load_token()
    
    def _load_token(self):
        """Load token from local storage"""
        if not self._local_storage:
            return
            
        try:
            token = self._local_storage.get(settings.TOKEN_KEY)
            if token:
                self.token = token
                
            # Load user data if available
            user_data = self._local_storage.get(settings.USER_KEY)
            if user_data:
                self._current_user = json.loads(user_data)
        except Exception as e:
            logger.error(f"Error loading auth data: {e}")
    
    def _save_user_data(self):
        """Save user data to local storage"""
        if not self._local_storage:
            return
            
        try:
            if self._current_user:
                self._local_storage.set(
                    settings.USER_KEY,
                    json.dumps(self._current_user, default=str)
                )
            else:
                self._local_storage.remove(settings.USER_KEY)
        except Exception as e:
            logger.error(f"Error saving user data: {e}")
    
    async def login(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate a user with email and password"""
        response = await super().login(email, password)
        
        if response.success and response.data:
            self._save_user_data()
            
        return response
    
    async def register(self, email: str, password: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new user"""
        response = await super().register(email, password, user_data)
        
        if response.success and response.data:
            self._save_user_data()
            
        return response
    
    def logout(self):
        """Log out the current user"""
        super().logout()
        if self._local_storage:
            self._local_storage.remove(settings.USER_KEY)
    
    async def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Get the current authenticated user"""
        if not self._current_user and self._local_storage:
            user_data = self._local_storage.get(settings.USER_KEY)
            if user_data:
                self._current_user = json.loads(user_data)
                
        return await super().get_current_user()

# Singleton instance
auth_service = PWAAuthService()

def get_auth_service() -> PWAAuthService:
    """Get the PWA auth service instance"""
    return auth_service
