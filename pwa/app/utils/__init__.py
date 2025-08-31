"""Utility functions for the PWA"""
import json
from datetime import datetime
from typing import Any, Dict, Optional, List, Union

# Type aliases
JSONType = Union[Dict[str, Any], List[Any], str, int, float, bool, None]

def format_currency(amount: float, currency: str = 'KES') -> str:
    """Format a number as a currency string"""
    return f"{currency} {amount:,.2f}"

def format_date(dt: Union[str, datetime], format_str: str = '%Y-%m-%d %H:%M') -> str:
    """Format a date or datetime string"""
    if isinstance(dt, str):
        # Try to parse the date string
        try:
            dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return dt
    
    if not isinstance(dt, datetime):
        return str(dt)
        
    return dt.strftime(format_str)

def parse_json_safe(json_str: str, default: Any = None) -> JSONType:
    """Safely parse a JSON string"""
    if not json_str:
        return default
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default

def to_camel_case(snake_str: str) -> str:
    """Convert snake_case to camelCase"""
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])

def to_snake_case(camel_str: str) -> str:
    """Convert camelCase to snake_case"""
    import re
    return re.sub(r'(?<!^)(?=[A-Z])', '_', camel_str).lower()

def get_error_message(error: Any, default: str = "An error occurred") -> str:
    """Extract a user-friendly error message from an error object"""
    if not error:
        return default
        
    if isinstance(error, str):
        return error
        
    if hasattr(error, 'get'):
        # Handle dict-like objects
        return error.get('message') or error.get('detail') or str(error)
        
    if hasattr(error, 'message'):
        return str(error.message)
        
    return str(error)
