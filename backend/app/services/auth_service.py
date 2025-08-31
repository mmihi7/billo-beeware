from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from supabase import create_client, Client as SupabaseClient
from app.core.config import settings

class AuthService:
    def __init__(self):
        self.supabase: SupabaseClient = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_ROLE_KEY
        )
    
    async def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate a user with email and password
        Returns user data if successful, None otherwise
        """
        try:
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            user = response.user
            session = response.session
            
            # Get user profile with role information
            profile = self.supabase.table('profiles') \
                .select('*') \
                .eq('id', user.id) \
                .single() \
                .execute()
            
            return {
                "id": user.id,
                "email": user.email,
                "role": profile.data.get('role', 'customer'),
                "restaurant_id": profile.data.get('restaurant_id'),
                "session": session
            }
            
        except Exception as e:
            print(f"Authentication error: {str(e)}")
            return None
    
    def get_user_by_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """
        Get user by session token (for web)
        """
        try:
            # Get user from session
            response = self.supabase.auth.get_user(session_token)
            user = response.user
            
            # Get user profile with role information
            profile = self.supabase.table('profiles') \
                .select('*') \
                .eq('id', user.id) \
                .single() \
                .execute()
            
            return {
                "id": user.id,
                "email": user.email,
                "role": profile.data.get('role', 'customer'),
                "restaurant_id": profile.data.get('restaurant_id')
            }
            
        except Exception as e:
            print(f"Session validation error: {str(e)}")
            return None
    
    def create_user(self, email: str, password: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new user with the given email, password, and additional data
        """
        try:
            # Create auth user
            auth_response = self.supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "full_name": user_data.get('full_name', ''),
                        "role": user_data.get('role', 'customer')
                    }
                }
            })
            
            # Create user profile
            profile_data = {
                "id": auth_response.user.id,
                "email": email,
                "role": user_data.get('role', 'customer'),
                "restaurant_id": user_data.get('restaurant_id')
            }
            
            self.supabase.table('profiles').insert(profile_data).execute()
            
            return {
                "id": auth_response.user.id,
                "email": email,
                "role": user_data.get('role', 'customer'),
                "restaurant_id": user_data.get('restaurant_id')
            }
            
        except Exception as e:
            print(f"User creation error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not create user"
            )

# Create a single instance of the auth service
auth_service = AuthService()
