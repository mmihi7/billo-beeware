from datetime import timedelta
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from app.core.jwt import create_access_token, create_refresh_token
from app.core.config import settings
from app.services.auth_service import auth_service

router = APIRouter()

class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str
    is_mobile: bool = False

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    role: str = "customer"
    restaurant_id: Optional[str] = None

@router.post("/login", response_model=Token)
async def login(
    request: Request,
    response: Response,
    user_data: UserLogin
):
    """
    Login endpoint that supports both web (session) and mobile (JWT) authentication
    """
    user = await auth_service.authenticate_user(user_data.email, user_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    if user_data.is_mobile:
        # For mobile: Return JWT tokens
        access_token = create_access_token(
            subject=user["id"],
            email=user["email"],
            role=user["role"],
            restaurant_id=user.get("restaurant_id")
        )
        
        refresh_token = create_refresh_token(
            subject=user["id"]
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "refresh_token": refresh_token
        }
    else:
        # For web: Set session cookie
        response.set_cookie(
            key="sb-access-token",
            value=user["session"].access_token,
            httponly=True,
            max_age=60 * 60 * 24 * 7,  # 7 days
            samesite="lax",
            secure=not settings.DEBUG
        )
        
        return {
            "access_token": user["session"].access_token,
            "token_type": "bearer"
        }

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """
    Register a new user
    """
    try:
        user = auth_service.create_user(
            email=user_data.email,
            password=user_data.password,
            user_data={
                "full_name": user_data.full_name,
                "role": user_data.role,
                "restaurant_id": user_data.restaurant_id
            }
        )
        return {"message": "User created successfully", "user_id": user["id"]}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/logout")
async def logout(response: Response):
    """
    Logout endpoint - clears the session cookie
    """
    response.delete_cookie("sb-access-token")
    return {"message": "Logged out successfully"}

@router.get("/me")
async def get_current_user(request: Request):
    """
    Get current user information
    """
    # For web: Get session from cookie
    session_token = request.cookies.get("sb-access-token")
    
    # For mobile: Get token from Authorization header
    if not session_token and "authorization" in request.headers:
        auth_header = request.headers["authorization"]
        if auth_header.startswith("Bearer "):
            session_token = auth_header.split(" ")[1]
    
    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    user = auth_service.get_user_by_session(session_token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session"
        )
    
    return user