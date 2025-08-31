import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import jwt
from ..config import settings
from ..models.base import ResponseModel
from ..utils.api_client import get_api_client

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self):
        self.api = get_api_client()
        self._current_user: Optional[Dict[str, Any]] = None
        self._token: Optional[str] = None
    
    @property
    def token(self) -> Optional[str]:
        """Get the current authentication token."""
        if not self._token:
            self._load_token()
        return self._token
    
    @token.setter
    def token(self, value: Optional[str]):
        """Set the authentication token and save it to storage."""
        self._token = value
        self._save_token()
        if value:
            self.api.token = value
        else:
            self._current_user = None
    
    def _load_token(self):
        """Load token from secure storage."""
        # This should be implemented by the platform-specific code
        # For web: localStorage/sessionStorage
        # For mobile: SecureStore/Keychain
        pass
    
    def _save_token(self):
        """Save token to secure storage."""
        # This should be implemented by the platform-specific code
        pass
    
    def _get_storage(self):
        """Get the appropriate storage based on the platform."""
        # This should be implemented by the platform-specific code
        # Return a dict-like object for storage
        pass
    
    async def login(self, email: str, password: str) -> ResponseModel[Dict[str, Any]]:
        """Authenticate a user with email and password."""
        try:
            response = await self.api.post(
                "auth/login",
                json={"email": email, "password": password}
            )
            
            if response.success and response.data:
                self.token = response.data.get("access_token")
                self._current_user = response.data.get("user")
                
            return response
            
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return ResponseModel(
                success=False,
                message="Login failed",
                error={"code": 500, "detail": str(e)}
            )
    
    async def register(self, email: str, password: str, user_data: Dict[str, Any]) -> ResponseModel[Dict[str, Any]]:
        """Register a new user."""
        try:
            data = {"email": email, "password": password, **user_data}
            response = await self.api.post("auth/register", json=data)
            
            if response.success and response.data:
                self.token = response.data.get("access_token")
                self._current_user = response.data.get("user")
                
            return response
            
        except Exception as e:
            logger.error(f"Registration failed: {e}")
            return ResponseModel(
                success=False,
                message="Registration failed",
                error={"code": 500, "detail": str(e)}
            )
    
    def logout(self):
        """Log out the current user."""
        self.token = None
        self._current_user = None
    
    def is_authenticated(self) -> bool:
        """Check if a user is currently authenticated."""
        if not self.token:
            return False
        
        try:
            # Verify the token is not expired
            payload = jwt.decode(
                self.token,
                settings.JWT_SECRET,
                algorithms=[settings.JWT_ALGORITHM]
            )
            return True
        except jwt.ExpiredSignatureError:
            return False
        except jwt.InvalidTokenError:
            return False
    
    async def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Get the current authenticated user."""
        if not self.is_authenticated():
            return None
            
        if not self._current_user:
            try:
                response = await self.api.get("auth/me")
                if response.success and response.data:
                    self._current_user = response.data
            except Exception as e:
                logger.error(f"Failed to fetch current user: {e}")
                
        return self._current_user

# Singleton instance
auth_service: Optional[AuthService] = None

def get_auth_service() -> AuthService:
    """Get or create the auth service instance."""
    global auth_service
    if auth_service is None:
        auth_service = AuthService()
    return auth_service
