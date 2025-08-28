from pydantic import BaseSettings, PostgresDsn, AnyHttpUrl
from typing import List, Optional
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Billo Restaurant POS"
    VERSION: str = "1.0.0"
    
    # Supabase Configuration
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    SUPABASE_JWT_SECRET: str = os.getenv("SUPABASE_JWT_SECRET", "")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    if not DATABASE_URL and SUPABASE_URL:
        # Construct Supabase Postgres URL if not provided
        db_url = SUPABASE_URL.replace("https://", "")
        db_user = "postgres"  # Default Supabase user
        db_pass = os.getenv("SUPABASE_DB_PASSWORD", "")
        db_host = db_url.split(".supabase.co")[0] + ".supabase.co"
        db_name = "postgres"  # Default Supabase database
        db_port = "5432"
        DATABASE_URL = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", SUPABASE_JWT_SECRET or "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",  # Frontend
        "http://localhost:8000",  # Backend
        "http://localhost:19006",  # React Native web
    ]
    
    # Business Rules
    TAB_NUMBER_PREFIX: str = os.getenv("TAB_NUMBER_PREFIX", "T")
    CURRENCY: str = os.getenv("CURRENCY", "KES")
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
