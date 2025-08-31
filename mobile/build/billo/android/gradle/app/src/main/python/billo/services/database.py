""
Database service for Supabase interactions.
"""
import logging
from typing import Any, Dict, List, Optional
from ..config.supabase import get_supabase

class DatabaseService:
    """Service for database operations using Supabase."""
    
    def __init__(self):
        self.supabase = get_supabase()
        self.logger = logging.getLogger(__name__)
    
    async def fetch_one(self, table: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Fetch a single record from a table."""
        try:
            query_builder = self.supabase.table(table).select('*')
            
            # Apply filters
            for key, value in query.items():
                if key == 'eq':
                    for field, val in value.items():
                        query_builder = query_builder.eq(field, val)
                # Add more filter types (gt, lt, etc.) as needed
                
            result = await query_builder.single().execute()
            return result.data if result.data else None
            
        except Exception as e:
            self.logger.error(f"Error fetching from {table}: {e}")
            return None
    
    async def fetch_all(self, table: str, query: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Fetch multiple records from a table."""
        try:
            query_builder = self.supabase.table(table).select('*')
            
            if query:
                for key, value in query.items():
                    if key == 'eq':
                        for field, val in value.items():
                            query_builder = query_builder.eq(field, val)
                    # Add more filter types as needed
            
            result = await query_builder.execute()
            return result.data if result.data else []
            
        except Exception as e:
            self.logger.error(f"Error fetching from {table}: {e}")
            return []
    
    async def insert(self, table: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Insert a new record into a table."""
        try:
            result = await self.supabase.table(table).insert(data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            self.logger.error(f"Error inserting into {table}: {e}")
            return None
    
    async def update(self, table: str, id: str, data: Dict[str, Any]) -> bool:
        """Update a record in a table."""
        try:
            result = await self.supabase.table(table).update(data).eq('id', id).execute()
            return bool(result.data)
        except Exception as e:
            self.logger.error(f"Error updating {table}: {e}")
            return False
    
    async def delete(self, table: str, id: str) -> bool:
        """Delete a record from a table."""
        try:
            result = await self.supabase.table(table).delete().eq('id', id).execute()
            return bool(result.data)
        except Exception as e:
            self.logger.error(f"Error deleting from {table}: {e}")
            return False
    
    # Restaurant-related methods
    async def get_restaurant_by_owner(self, owner_id: str) -> Optional[Dict[str, Any]]:
        """Get restaurant by owner ID."""
        return await self.fetch_one('restaurants', {'eq': {'owner_id': owner_id}})
    
    async def get_menu_items(self, restaurant_id: str) -> List[Dict[str, Any]]:
        """Get menu items for a restaurant."""
        return await self.fetch_all('menu_items', {'eq': {'restaurant_id': restaurant_id}})
    
    async def get_active_orders(self, restaurant_id: str) -> List[Dict[str, Any]]:
        """Get active orders for a restaurant."""
        return await self.fetch_all('orders', {
            'eq': {
                'restaurant_id': restaurant_id,
                'status': 'active'
            }
        })

# Singleton instance
db_service = DatabaseService()

def get_database() -> DatabaseService:
    """Get the database service instance."""
    return db_service
