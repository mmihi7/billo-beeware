import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path('..') / '.env'
load_dotenv(dotenv_path=env_path)

class PWASettings:
    # API Configuration
    API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')
    API_VERSION = os.getenv('API_VERSION', 'v1')
    
    # WebSocket Configuration
    WS_BASE_URL = os.getenv('WS_BASE_URL', 'ws://localhost:8000')
    
    # Authentication
    TOKEN_KEY = 'billo_auth_token'
    USER_KEY = 'billo_user_data'
    
    # Local Storage Keys
    CART_KEY = 'billo_cart'
    RESTAURANT_KEY = 'billo_restaurant'

# Initialize settings
settings = PWASettings()
