import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from ..config.supabase import get_supabase

class AuthService:
    def __init__(self):
        self.supabase = get_supabase()
        self.current_user: Optional[Dict[str, Any]] = None
        self.session = None
        self.logger = logging.getLogger(__name__)
        self._load_session()
    
    def _save_session(self):
        """Save session data to secure storage"""
        if not self.session:
            return
            
        session_data = {
            'access_token': self.session.access_token,
            'refresh_token': self.session.refresh_token,
            'user': self.session.user.model_dump() if self.session.user else None,
            'expires_at': self.session.expires_at.isoformat() if self.session.expires_at else None
        }
        
        try:
            # Use secure storage in production
            import toga
            toga.App.app.preferences['supabase_session'] = json.dumps(session_data)
        except Exception as e:
            self.logger.error(f"Failed to save session: {e}")
    
    def _load_session(self):
        """Load session data from secure storage"""
        try:
            import toga
            session_data = toga.App.app.preferences.get('supabase_session')
            if not session_data:
                return
                
            session_data = json.loads(session_data)
            if not all(k in session_data for k in ['access_token', 'refresh_token', 'user']):
                return
                
            # Check if session is expired
            if session_data.get('expires_at'):
                expires_at = datetime.fromisoformat(session_data['expires_at'])
                if datetime.utcnow() >= expires_at - timedelta(minutes=5):  # Refresh if expiring soon
                    self._refresh_session(session_data['refresh_token'])
                    return
            
            from gotrue import Session
            self.session = Session(
                access_token=session_data['access_token'],
                refresh_token=session_data['refresh_token'],
                user=self.supabase.auth._get_user_attributes(session_data['user']),
                expires_at=session_data.get('expires_at')
            )
            self.current_user = session_data['user']
            
        except Exception as e:
            self.logger.error(f"Failed to load session: {e}")
    
    async def _refresh_session(self, refresh_token: str = None):
        """Refresh the current session"""
        try:
            if not refresh_token and self.session:
                refresh_token = self.session.refresh_token
                
            if not refresh_token:
                return False
                
            response = self.supabase.auth.refresh_session(refresh_token)
            if not response.session:
                return False
                
            self.session = response.session
            self.current_user = response.user.model_dump() if response.user else None
            self._save_session()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to refresh session: {e}")
            return False
            session_data = json.loads(toga.App.app.preferences.get('session', '{}'))
            if session_data.get('token'):
                self.api.token = session_data['token']
                self.current_user = session_data.get('user')
                return True
        except Exception as e:
            self.logger.error(f"Failed to load session: {e}")
        return False
    
    async def login(self, email: str, password: str) -> bool:
        """Attempt to log in with email and password"""
        try:
            response = await self.api.login(email, password)
            if self.api.token:
                # Get user profile
                self.current_user = {
                    'id': response.get('user_id'),
                    'email': email,
                    'name': response.get('name', email.split('@')[0])
                }
                self._save_session()
        except Exception as e:
            self.logger.error(f"Login failed: {e}")
            return False
    
    async def signup(self, email: str, password: str, user_data: dict) -> bool:
        """Create a new user account"""
        try:
            response = await self.supabase.auth.sign_up({
                'email': email,
                'password': password,
                'options': {
                    'data': {
                        'full_name': user_data.get('full_name', ''),
                        'role': user_data.get('role', 'customer')
                    }
                }
            })
            
            if not response.user:
                return False
                
            # Create user profile in the database
            profile_data = {
                'user_id': response.user.id,
                'email': email,
                'full_name': user_data.get('full_name', ''),
                'role': user_data.get('role', 'customer')
            }
            
            result = await self.supabase.table('profiles').insert(profile_data).execute()
            return bool(result.data)
            
        except Exception as e:
            self.logger.error(f"Signup failed: {e}")
            return False
    
    async def logout(self) -> bool:
        """Log out the current user"""
        try:
            if self.session:
                await self.supabase.auth.sign_out()
            
            self.session = None
            self.current_user = None
            
            # Clear session from storage
            try:
                import toga
                toga.App.app.preferences.remove('supabase_session')
            except Exception as e:
                self.logger.error(f"Failed to clear session: {e}")
                
            return True
            
        except Exception as e:
            self.logger.error(f"Logout failed: {e}")
            return False
    
    def is_authenticated(self) -> bool:
        """Check if a user is currently authenticated"""
        if not self.session or not self.current_user:
            return False
            
        # Check if session is expired
        if self.session.expires_at and datetime.utcnow() >= self.session.expires_at - timedelta(minutes=5):
            return False
            
        return True
    
    def get_user(self) -> Optional[Dict[str, Any]]:
        """Get the current user"""
        return self.current_user
    
    async def reset_password(self, email: str) -> bool:
        """Send password reset email"""
        try:
            await self.supabase.auth.reset_password_for_email(email)
            return True
        except Exception as e:
            self.logger.error(f"Password reset failed: {e}")
            return False

# Singleton instance
auth_service: Optional[AuthService] = None

def get_auth_service() -> AuthService:
    """Get the auth service instance"""
    global auth_service
    if auth_service is None:
        auth_service = AuthService()
    return auth_service
