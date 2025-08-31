"""
Supabase configuration for the Billo mobile app.
"""
import os
from supabase import create_client, Client
from typing import Tuple, Optional

class SupabaseConfig:
    """Configuration for Supabase client."""
    
    def __init__(self):
        self.url: str = os.getenv('SUPABASE_URL', 'YOUR_SUPABASE_URL')
        self.key: str = os.getenv('SUPABASE_KEY', 'YOUR_SUPABASE_ANON_KEY')
        self.client: Optional[Client] = None
        
    def get_client(self) -> Client:
        """Get or create a Supabase client instance."""
        if not self.client:
            if not self.url or not self.key:
                raise ValueError("Supabase URL and Key must be set in environment variables")
            self.client = create_client(self.url, self.key)
        return self.client
    
    @staticmethod
    def get_tables() -> dict:
        """Define Supabase tables and their RLS policies."""
        return {
            'profiles': {
                'select': 'user_id, username, full_name, avatar_url, role, created_at',
                'insert': 'user_id, username, full_name, avatar_url, role',
                'update': 'username, full_name, avatar_url, role',
                'policies': {
                    'select': 'auth.uid() = user_id',
                    'insert': 'auth.role() = \'authenticated\'',
                    'update': 'auth.uid() = user_id',
                }
            },
            'restaurants': {
                'select': 'id, name, address, phone, email, logo_url, owner_id, created_at',
                'insert': 'name, address, phone, email, logo_url, owner_id',
                'update': 'name, address, phone, email, logo_url',
                'policies': {
                    'select': 'auth.role() = \'service_role\' OR auth.uid() = owner_id',
                    'insert': 'auth.role() = \'authenticated\'',
                    'update': 'auth.uid() = owner_id',
                }
            },
            # Add more tables as needed
        }

# Singleton instance
supabase_config = SupabaseConfig()

def get_supabase() -> Client:
    """Get the Supabase client instance."""
    return supabase_config.get_client()
