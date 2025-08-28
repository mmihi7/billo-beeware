from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Dummy user database (replace with real database in production)
fake_users_db = {
    "admin@billo.app": {
        "username": "admin",
        "email": "admin@billo.app",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "secret"
        "disabled": False,
    }
}

class TokenData:
    def __init__(self, email: Optional[str] = None):
        self.email = email

class User:
    def __init__(self, username: str, email: str, hashed_password: str, disabled: bool = False):
        self.username = username
        self.email = email
        self.hashed_password = hashed_password
        self.disabled = disabled

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(email: str) -> Optional[User]:
    """Retrieve a user by email from the database.
    
    Args:
        email: The email of the user to retrieve
        
    Returns:
        User object if found, None otherwise
    """
    if not email:
        return None
        
    # In a real app, this would query your database
    if email in fake_users_db:
        user_data = fake_users_db[email]
        return User(
            username=user_data["username"],
            email=email,
            hashed_password=user_data["hashed_password"],
            disabled=user_data.get("disabled", False)
        )
    return None

def authenticate_user(email: str, password: str) -> Optional[User]:
    """Authenticate a user with email and password.
    
    Args:
        email: User's email
        password: Plain text password
        
    Returns:
        User object if authentication succeeds, None otherwise
    """
    if not email or not password:
        return None
        
    user = get_user(email)
    if not user:
        # Use a constant-time comparison to prevent timing attacks
        verify_password("dummy_password", "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW")
        return None
        
    if not verify_password(password, user.hashed_password):
        return None
        
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(request: Request):
    # Check for session-based authentication
    user_data = request.session.get("user")
    if not user_data or not user_data.get("is_authenticated"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"Location": "/login"}
        )
    
    # Get user from database
    user = get_user(email=user_data.get("email"))
    if not user:
        # Clear invalid session if user not found
        request.session.clear()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"Location": "/login"}
        )
        
    return user

async def get_current_active_user(request: Request) -> User:
    """Get the current active user from the session.
    
    Args:
        request: The FastAPI request object
        
    Returns:
        The authenticated User object
        
    Raises:
        HTTPException: If user is not authenticated or inactive
    """
    try:
        current_user = await get_current_user(request)
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"Location": "/login"}
            )
            
        if hasattr(current_user, 'disabled') and current_user.disabled:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user"
            )
            
        return current_user
        
    except HTTPException:
        raise
    except Exception as e:
        # Log the error in production
        print(f"Error in get_current_active_user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while authenticating"
        )
