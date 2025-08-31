import json
import logging
from typing import Optional, Dict, Any, Tuple, cast
from datetime import datetime, timedelta
from gotrue import Session, User
from supabase import Client
from ..config.supabase import get_supabase, get_auth

class AuthService:
    def __init__(self):
        self.supabase: Client = get_supabase()
        self.auth = get_auth()
        self.current_user: Optional[Dict[str, Any]] = None
        self.session: Optional[Session] = None
        self.logger = logging.getLogger(__name__)
        
        # Initialize the session
        import asyncio
        asyncio.get_event_loop().run_until_complete(self._load_session())
        
    async def sign_in(self, email: str, password: str) -> Tuple[bool, str]:
        """Sign in a user with email and password."""
        try:
            response = await self.auth.sign_in_with_password({"email": email, "password": password})
            if not response or not response.session:
                return False, "Invalid response from server"
                
            self.session = response.session
            self.current_user = response.user.dict() if response.user else None
            await self._save_session()
            return True, "Successfully signed in"
            
        except Exception as e:
            self.logger.error(f"Sign in failed: {str(e)}", exc_info=True)
            return False, str(e)
            
    async def sign_up(self, email: str, password: str, user_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Register a new user with email and password."""
        try:
            # Create the auth user
            auth_response = await self.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "full_name": user_data.get('full_name', ''),
                        "username": user_data.get('username', '')
                    }
                }
            })
            
            # Create the user profile in the database
            if auth_response.user:
                profile_data = {
                    'user_id': auth_response.user.id,
                    'email': email,
                    **user_data
                }
                
                # Insert the profile
                result = self.supabase.table('profiles').insert(profile_data).execute()
                if result.data:
                    self.session = auth_response.session
                    self.current_user = auth_response.user.dict()
                    await self._save_session()
                    return True, "Account created successfully"
            
            return False, "Failed to create user profile"
            
        except Exception as e:
            self.logger.error(f"Sign up failed: {str(e)}", exc_info=True)
            return False, str(e)
            
    async def sign_out(self) -> bool:
        """Sign out the current user."""
        try:
            if self.session:
                await self.auth.sign_out()
            await self._clear_session()
            return True
        except Exception as e:
            self.logger.error(f"Sign out failed: {str(e)}", exc_info=True)
            await self._clear_session()  # Ensure we clear session even on error
            return False
            
    async def reset_password(self, email: str) -> Tuple[bool, str]:
        """Send a password reset email."""
        try:
            await self.auth.reset_password_for_email(email)
            return True, "Password reset email sent"
        except Exception as e:
            self.logger.error(f"Password reset failed: {str(e)}", exc_info=True)
            return False, str(e)
            
    def is_authenticated(self) -> bool:
        """Check if a user is currently authenticated."""
        if not self.session:
            return False
            
        # Check if session is expired
        if self.session.expires_at and datetime.utcnow() >= self.session.expires_at - timedelta(minutes=5):
            return False
            
        return True
    
    async def _save_session(self) -> bool:
        """Save session data to secure storage"""
        if not self.session:
            return False
            
        try:
            session_data = {
                'access_token': self.session.access_token,
                'refresh_token': self.session.refresh_token,
                'user': self.session.user.dict() if self.session.user else None,
                'expires_at': self.session.expires_at.isoformat() if self.session.expires_at else None
            }
            
            # Use secure storage in production
            import toga
            toga.App.app.preferences['supabase_session'] = json.dumps(session_data)
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save session: {e}", exc_info=True)
            return False
    
    async def _refresh_session(self, refresh_token: str) -> bool:
        """Refresh the current session using the refresh token."""
        try:
            response = await self.auth.refresh_session(refresh_token)
            if not response or not response.session:
                self.logger.error("Failed to refresh session: Invalid response")
                await self._clear_session()
                return False
                
            self.session = response.session
            self.current_user = response.user.dict() if response.user else None
            await self._save_session()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to refresh session: {e}", exc_info=True)
            await self._clear_session()
            return False
            
    async def _load_session(self) -> bool:
        """Load session data from secure storage"""
        try:
            import toga
            session_data = toga.App.app.preferences.get('supabase_session')
            if not session_data:
                return False
                
            session_data = json.loads(session_data)
            if not all(k in session_data for k in ['access_token', 'refresh_token', 'user']):
                return False
                
            # Check if session is expired
            if session_data.get('expires_at'):
                expires_at = datetime.fromisoformat(session_data['expires_at'])
                if datetime.utcnow() >= expires_at - timedelta(minutes=5):
                    # Try to refresh the session
                    return await self._refresh_session(session_data['refresh_token'])
            
            # Restore session
            self.session = Session(
                access_token=session_data['access_token'],
                refresh_token=session_data['refresh_token'],
                user=session_data['user'],
                expires_at=datetime.fromisoformat(session_data['expires_at']) if session_data.get('expires_at') else None
            )
            self.current_user = session_data.get('user')
            return True
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid session data format: {e}")
            await self._clear_session()
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to load session: {e}", exc_info=True)
            await self._clear_session()
            return False
    
    async def _clear_session(self) -> None:
        """Clear the current session and user data."""
        try:
            import toga
            if 'supabase_session' in toga.App.app.preferences:
                del toga.App.app.preferences['supabase_session']
        except Exception as e:
            self.logger.error(f"Failed to clear session: {e}", exc_info=True)
        finally:
            self.session = None
            self.current_user = None

    def get_user(self) -> Optional[Dict[str, Any]]:
        """Get the current user"""
        return self.current_user

# Singleton instance
auth_service: Optional[AuthService] = None

def get_auth_service() -> AuthService:
    """Get the auth service instance."""
    global auth_service
    if auth_service is None:
        auth_service = AuthService()
    return auth_service
