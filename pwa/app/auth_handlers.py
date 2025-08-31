from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import os
from dotenv import load_dotenv
from supabase import create_client, Client as SupabaseClient

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase: SupabaseClient = create_client(
    supabase_url=os.getenv("SUPABASE_URL"),
    supabase_key=os.getenv("SUPABASE_ANON_KEY")
)

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
router = APIRouter()

# JWT Token Functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Get user from Supabase
    user = supabase.auth.get_user(token)
    if user is None:
        raise credentials_exception
    return user

# Auth Routes
@router.post("/auth/register")
async def register_user(
    email: str, 
    password: str, 
    full_name: str,
    role: str = "customer"
):
    """Register a new user with Supabase"""
    try:
        # Create user in Supabase Auth
        auth_response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "full_name": full_name,
                    "role": role
                }
            }
        })
        
        if not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user"
            )
        
        # Create user profile in the database
        profile_data = {
            "id": str(auth_response.user.id),
            "email": email,
            "full_name": full_name,
            "role": role
        }
        
        # Insert into profiles table
        supabase.table("profiles").insert(profile_data).execute()
        
        return {"message": "User registered successfully", "user_id": auth_response.user.id}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/auth/login")
async def login_user(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """Login user with email and password"""
    try:
        # Authenticate with Supabase
        auth_response = supabase.auth.sign_in_with_password({
            "email": form_data.username,
            "password": form_data.password
        })
        
        if not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Create JWT token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": auth_response.user.id},
            expires_delta=access_token_expires
        )
        
        # Get user profile
        profile = supabase.table("profiles").select("*").eq("id", auth_response.user.id).single().execute()
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": profile.data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

@router.post("/auth/logout")
async def logout_user():
    """Logout the current user"""
    try:
        supabase.auth.sign_out()
        return {"message": "Successfully logged out"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/auth/me")
async def get_current_user_profile(current_user = Depends(get_current_user)):
    """Get current user's profile"""
    try:
        profile = supabase.table("profiles").select("*").eq("id", current_user.user.id).single().execute()
        return profile.data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found"
        )

# Password Reset
@router.post("/auth/forgot-password")
async def forgot_password(email: str):
    """Send password reset email"""
    try:
        reset_link = f"{os.getenv('FRONTEND_URL')}/reset-password"
        supabase.auth.reset_password_for_email(email, {"redirect_to": reset_link})
        return {"message": "Password reset email sent"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/auth/reset-password")
async def reset_password(
    token: str,
    new_password: str
):
    """Reset user password with token"""
    try:
        # Supabase handles password reset through email link
        # This endpoint would be called after user clicks the reset link
        supabase.auth.update_user({
            "password": new_password
        })
        return {"message": "Password updated successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
