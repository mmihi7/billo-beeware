"""
Supabase configuration for the Billo mobile app.
"""
import os
import logging
from typing import Optional, Dict, Any

from supabase import create_client, Client
from gotrue import Session


logger = logging.getLogger(__name__)

# Debug: Print all environment variables
def debug_env():
    logger.info("=== Environment Variables ===")
    for key, value in os.environ.items():
        # Don't log the actual key value for security
        if 'KEY' in key.upper():
            logger.info(f"{key}: ***REDACTED***")
        else:
            logger.info(f"{key}: {value}")
    logger.info("============================")

# Call debug function
debug_env()

# Hardcoded fallback values (for debugging)
SUPABASE_URL_DEFAULT = "https://fqjvwnbrhfctknlrpyba.supabase.co"
SUPABASE_KEY_DEFAULT = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZxanZ3bmJyaGZjdGtubHJweWJhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTYyMTYzMzgsImV4cCI6MjA3MTc5MjMzOH0.MEJwtBrmzGpv0JobWoA2W0RaunyiQ50gYmkP8oSaC1g"

class SupabaseConfig:
    """Configuration for Supabase client."""

    def __init__(self):
        # Try environment variables first, then fallback to defaults
        self.url: str = os.getenv("SUPABASE_URL", SUPABASE_URL_DEFAULT)
        self.key: str = os.getenv("SUPABASE_KEY", SUPABASE_KEY_DEFAULT)
        self.client: Optional[Client] = None
        
        logger.info(f"Supabase URL found: {bool(self.url)}")
        logger.info(f"Supabase Key found: {bool(self.key) and '***REDACTED***'}")


    def get_client(self) -> Client:
        """Get or create a Supabase client instance."""
        if not self.client:
            if not self.url or not self.key:
                raise ValueError(
                    f"Supabase URL and Key must be set. URL: {bool(self.url)}, Key: {bool(self.key)}"
                )
            logger.info("Creating Supabase client...")
            self.client = create_client(self.url, self.key)

            # Set up auth state change listener
            def on_auth_state_change(event: str, session: Optional[Session]) -> None:
                if event == "TOKEN_REFRESHED":
                    logger.info("Auth token refreshed")
                elif event == "SIGNED_IN" and session and session.user:
                    logger.info(f"User signed in: {session.user.email}")
                elif event == "SIGNED_OUT":
                    logger.info("User signed out")

            self.client.auth.on_auth_state_change(on_auth_state_change)

        return self.client

    @staticmethod
    def get_tables() -> Dict[str, Dict[str, Any]]:
        """Define Supabase tables and their RLS policies."""
        return {
            "profiles": {
                "select": "id, email, full_name, pin, role, restaurant_id, created_at",
                "insert": "email, full_name, pin, role, restaurant_id",
                "update": "full_name, pin, role, restaurant_id",
                "policies": {
                    "select": """
                    auth.role() = 'service_role' OR auth.uid() = id OR (
                        EXISTS (
                            SELECT 1 FROM profiles 
                            WHERE id = auth.uid() AND (
                                role = 'admin' OR 
                                (role = 'waiter' AND restaurant_id = profiles.restaurant_id)
                            )
                        )
                    )
                    """.strip(),
                    "insert": """
                        auth.role() = 'service_role' OR (
                            EXISTS (
                                SELECT 1 FROM profiles 
                                WHERE id = auth.uid() AND role = 'admin' AND restaurant_id = profiles.restaurant_id
                            )
                        )
                        """.strip(),
                    "update": """
                        auth.role() = 'service_role' OR auth.uid() = id OR (
                            EXISTS (
                                SELECT 1 FROM profiles 
                                WHERE id = auth.uid() AND role = 'admin' AND restaurant_id = profiles.restaurant_id
                            )
                        )
                        """.strip(),
                    "delete": "auth.role() = 'service_role'"
                }
            },
            "restaurants": {
                "select": "id, name, address, phone, is_active, created_by, created_at",
                "insert": "name, address, phone, is_active, created_by",
                "update": "name, address, phone, is_active",
                "policies": {
                    "select": """
                        auth.role() = 'service_role' OR EXISTS (
                            SELECT 1 FROM profiles 
                            WHERE id = auth.uid() AND (
                                role = 'admin' OR 
                                (role IN ('waiter', 'customer') AND restaurant_id = restaurants.id)
                            )
                        )
                        """.strip(),
                    "insert": """
                        auth.role() = 'service_role' OR (
                            EXISTS (
                                SELECT 1 FROM profiles 
                                WHERE id = auth.uid() AND role = 'admin'
                            )
                        )
                        """.strip(),
                    "update": """
                        auth.role() = 'service_role' OR (
                            EXISTS (
                                SELECT 1 FROM profiles 
                                WHERE id = auth.uid() AND role = 'admin' AND restaurant_id = restaurants.id
                            )
                        )
                        """.strip(),
                    "delete": "FALSE"  # Only service_role can delete restaurants
                }
            },
            "business_hours": {
                "select": "id, restaurant_id, day_of_week, open_time, close_time, is_closed",
                "insert": "restaurant_id, day_of_week, open_time, close_time, is_closed",
                "update": "day_of_week, open_time, close_time, is_closed",
                "policies": {
                    "select": """
                        auth.role() = 'service_role' OR EXISTS (
                            SELECT 1 FROM profiles p 
                            WHERE p.id = auth.uid() AND p.restaurant_id = business_hours.restaurant_id
                        )
                        """.strip(),
                    "insert": """
                        auth.role() = 'service_role' OR (
                            EXISTS (
                                SELECT 1 FROM profiles 
                                WHERE id = auth.uid() AND role = 'admin' 
                                AND restaurant_id = business_hours.restaurant_id
                            )
                        )
                        """.strip(),
                    "update": """
                        auth.role() = 'service_role' OR (
                            EXISTS (
                                SELECT 1 FROM profiles 
                                WHERE id = auth.uid() AND role = 'admin' 
                                AND restaurant_id = business_hours.restaurant_id
                            )
                        )
                        """.strip()
                }
            },
            "tabs": {
                "select": "id, restaurant_id, tab_number, status, opened_by, created_at, updated_at, tab_date",
                "insert": "restaurant_id, tab_number, status, opened_by, tab_date",
                "update": "status, updated_at = NOW()",
                "policies": {
                    "select": """
                        auth.role() = 'service_role' OR EXISTS (
                            SELECT 1 FROM profiles p 
                            WHERE p.id = auth.uid() AND (
                                p.role = 'admin' OR 
                                (p.role = 'waiter' AND p.restaurant_id = tabs.restaurant_id) OR
                                (p.role = 'customer' AND p.id = tabs.opened_by)
                            )
                        )
                        """.strip(),
                    "insert": """
                        auth.role() = 'service_role' OR (
                            SELECT role FROM profiles WHERE id = auth.uid()
                        ) IN ('admin', 'waiter', 'customer')
                        """.strip(),
                    "update": """
                        auth.role() = 'service_role' OR (
                            SELECT role FROM profiles WHERE id = auth.uid()
                        ) IN ('admin', 'waiter')
                        """.strip(),
                    "delete": "FALSE"  # Only service_role can delete tabs
                }
            },
            "menu_items": {
                "select": "id, restaurant_id, name, description, price, category, is_available, is_featured, image_url, created_at",
                "insert": "restaurant_id, name, description, price, category, is_available, is_featured, image_url",
                "update": "name, description, price, category, is_available, is_featured, image_url",
                "policies": {
                    "select": """
                        auth.role() = 'service_role' OR EXISTS (
                            SELECT 1 FROM profiles p 
                            WHERE p.id = auth.uid() AND p.restaurant_id = menu_items.restaurant_id
                        )
                        """.strip(),
                    "insert": """
                        auth.role() = 'service_role' OR (
                            SELECT role FROM profiles WHERE id = auth.uid()
                        ) IN ('admin', 'waiter')
                        """.strip(),
                    "update": """
                        auth.role() = 'service_role' OR (
                            SELECT role FROM profiles WHERE id = auth.uid()
                        ) IN ('admin', 'waiter')
                        """.strip(),
                    "delete": "FALSE"  # Only service_role can delete menu items
                }
            },
            "orders": {
                "select": "id, tab_id, menu_item_id, quantity, status, notes, created_at, updated_at",
                "insert": "tab_id, menu_item_id, quantity, status, notes",
                "update": "quantity, status, notes, updated_at = NOW()",
                "policies": {
                    "select": """
                        auth.role() = 'service_role' OR EXISTS (
                            SELECT 1 FROM tabs t
                            JOIN profiles p ON p.id = t.opened_by
                            WHERE t.id = orders.tab_id AND (
                                p.id = auth.uid() OR
                                (p.restaurant_id = (SELECT restaurant_id FROM tabs WHERE id = orders.tab_id) AND p.role IN ('admin', 'waiter'))
                            )
                        )
                        """.strip(),
                    "insert": """
                        auth.role() = 'service_role' OR (
                            SELECT role FROM profiles WHERE id = auth.uid()
                        ) IN ('admin', 'waiter')
                        """.strip(),
                    "update": """
                        auth.role() = 'service_role' OR (
                            SELECT role FROM profiles WHERE id = auth.uid()
                        ) IN ('admin', 'waiter')
                        """.strip(),
                    "delete": "FALSE"  # Only service_role can delete orders
                }
            },
            "promos": {
                "select": "id, restaurant_id, name, description, code, discount_type, discount_value, min_order_amount, max_discount, start_date, end_date, is_active, created_at",
                "insert": "restaurant_id, name, description, code, discount_type, discount_value, min_order_amount, max_discount, start_date, end_date, is_active",
                "update": "name, description, code, discount_type, discount_value, min_order_amount, max_discount, start_date, end_date, is_active",
                "policies": {
                    "select": """
                        auth.role() = 'service_role' OR EXISTS (
                            SELECT 1 FROM profiles p 
                            WHERE p.id = auth.uid() AND p.restaurant_id = promos.restaurant_id
                        )
                        """.strip(),
                    "insert": """
                        auth.role() = 'service_role' OR (
                            SELECT role FROM profiles WHERE id = auth.uid()
                        ) = 'admin'
                        """.strip(),
                    "update": """
                        auth.role() = 'service_role' OR (
                            SELECT role FROM profiles WHERE id = auth.uid()
                        ) = 'admin'
                        """.strip()
                }
            },
            "chats": {
                "select": "id, tab_id, sender_id, message, created_at",
                "insert": "tab_id, sender_id, message",
                "policies": {
                    "select": """
                        auth.role() = 'service_role' OR EXISTS (
                            SELECT 1 FROM tabs t
                            JOIN profiles p ON p.id = t.opened_by
                            WHERE t.id = chats.tab_id AND (
                                p.id = auth.uid() OR
                                (p.restaurant_id = (SELECT restaurant_id FROM tabs WHERE id = chats.tab_id) AND p.role IN ('admin', 'waiter'))
                            )
                        )
                        """.strip(),
                    "insert": """
                        auth.role() = 'service_role' OR (
                            SELECT role FROM profiles WHERE id = auth.uid()
                        ) IN ('admin', 'waiter', 'customer')
                        """.strip(),
                    "delete": "FALSE"  # Only service_role can delete chat messages
                }
            }
        }


# Singleton instance
supabase_config = SupabaseConfig()


def get_supabase() -> Client:
    """Get the Supabase client instance."""
    return supabase_config.get_client()


def get_auth():
    """Get the Supabase auth instance."""
    return get_supabase().auth