from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, date
from typing import Optional, List
import os
from pathlib import Path

# Initialize FastAPI app
app = FastAPI(title="Billo Restaurant Management", version="1.0.0")

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up templates
templates = Jinja2Templates(directory="templates")

# Mount static files
static_dir = Path("static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Mock data - Replace with database calls
def get_restaurant_data(restaurant_id: str = "default"):
    return {
        "restaurant_name": "Billo Restaurant",
        "restaurant_id": restaurant_id,
        "stats": {
            "tables_occupied": 5,
            "tables_available": 15,
            "orders_today": 42,
            "revenue_today": 125000  # in cents
        }
    }

from supabase import create_client, Client
from app.services.config import settings

# Initialize Supabase client
def get_supabase() -> Client:
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)

# Authentication middleware
async def get_current_user(request: Request):
    # Check for auth token in cookies
    token = request.cookies.get("sb-access-token")
    
    if not token:
        # Check for token in Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
    
    if not token:
        # No token found, user is not authenticated
        return None
    
    try:
        # Verify the token with Supabase
        supabase = get_supabase()
        user = supabase.auth.get_user(token)
        if not user or not user.user:
            return None
        return user.user
    except Exception as e:
        print(f"Error verifying token: {e}")
        return None
        profile = supabase.table("profiles").select("*").eq("id", user.id).single().execute()
        
        if not profile.data:
            raise HTTPException(status_code=403, detail="User profile not found")
            
        return {
            "id": user.id,
            "email": user.email,
            "role": profile.data.get("role", "customer"),
            "name": profile.data.get("full_name", user.email.split("@")[0])
        }
        
    except Exception as e:
        print(f"Authentication error: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid authentication")

# Routes
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    # Check if user is already authenticated
    try:
        # This will raise an exception if not authenticated
        user = await get_current_user(request)
        # If we get here, user is authenticated, redirect to dashboard
        return RedirectResponse(url="/dashboard")
    except:
        # If not authenticated, show welcome page
        return templates.TemplateResponse(
            "welcome.html",
            {"request": request, "title": "Welcome to Billo"}
        )

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "title": "Login to Billo"}
    )

@app.post("/api/auth/login")
async def login_user(
    email: str = Form(...),
    password: str = Form(...)
):
    try:
        # Get Supabase client
        supabase = get_supabase()
        
        # Authenticate with Supabase
        auth_response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if not auth_response.user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Create response with redirect
        response = RedirectResponse("/dashboard", status_code=303)
        
        # Set the access token in an HTTP-only cookie
        response.set_cookie(
            key="sb-access-token",
            value=auth_response.session.access_token,
            httponly=True,
            max_age=auth_response.session.expires_in,
            samesite="lax",
            secure=True
        )
        
        return response
        
    except Exception as e:
        print(f"Login error: {str(e)}")
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid email or password"}
        )

@app.get("/logout")
async def logout():
    try:
        # Clear the Supabase session
        supabase = get_supabase()
        await supabase.auth.sign_out()
        
        # Create response with redirect to login
        response = RedirectResponse("/login")
        
        # Clear the auth cookie
        response.delete_cookie(
            key="sb-access-token",
            httponly=True,
            samesite="lax",
            secure=True
        )
        
        return response
    except Exception as e:
        print(f"Logout error: {str(e)}")
        # Still redirect to login even if logout fails
        return RedirectResponse("/login")

@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse(
        "signup.html",
        {"request": request, "title": "Create an Account"}
    )

@app.post("/api/auth/signup")
async def signup_user(
    email: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(...)
):
    try:
        supabase = get_supabase()
        
        # Create user in Supabase Auth
        auth_response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "full_name": full_name,
                    "role": "customer"  # Default role
                }
            }
        })
        
        if not auth_response.user:
            raise HTTPException(status_code=400, detail="Failed to create user account")
        
        # Create a profile in the database
        profile_data = {
            "id": auth_response.user.id,
            "email": email,
            "full_name": full_name,
            "role": "customer"
        }
        
        # Insert profile into profiles table
        supabase.table("profiles").insert(profile_data).execute()
        
        # Auto-login the user after signup
        login_response = await login_user(email, password)
        return login_response
        
    except Exception as e:
        print(f"Signup error: {str(e)}")
        return JSONResponse(
            status_code=400,
            content={"error": "Failed to create account. Please try again."}
        )

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, user: dict = Depends(get_current_user)):
    restaurant_data = get_restaurant_data()
    
    # Mock data for active tables
    active_tables = [
        {"id": i, "number": i, "status": "occupied" if i % 2 == 0 else "available", "order_count": i % 3 + 1}
        for i in range(1, 6)
    ]
    
    # Mock recent orders
    recent_orders = [
        {"id": 100 + i, "table": (i % 5) + 1, "items": (i % 3) + 1, "amount": 2500 * (i + 1), "status": "preparing"}
        for i in range(5)
    ]
    
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "restaurant_name": restaurant_data["restaurant_name"],
            "stats": restaurant_data["stats"],
            "active_tables": active_tables,
            "recent_orders": recent_orders,
            "user": user
        }
    )

@app.get("/orders", response_class=HTMLResponse)
async def orders(
    request: Request,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
    user: dict = Depends(get_current_user)
):
    # Mock orders data - Replace with database query
    all_orders = [
        {
            "id": 100 + i,
            "table_number": (i % 5) + 1,
            "status": ["pending", "preparing", "ready", "completed", "cancelled"][i % 5],
            "created_at": datetime(2023, 8, (i % 28) + 1, 10 + (i % 8), 30 + (i * 10) % 30),
            "items": [
                {"name": f"Item {j+1}", "quantity": (i % 3) + 1, "price": 1000 * (j + 1)}
                for j in range((i % 3) + 1)
            ],
            "total_amount": 2500 * (i + 1)
        }
        for i in range(50)
    ]
    
    # Filter by status if provided
    if status:
        all_orders = [o for o in all_orders if o["status"] == status]
    
    # Pagination
    start = (page - 1) * page_size
    end = start + page_size
    orders_page = all_orders[start:end]
    total_pages = (len(all_orders) + page_size - 1) // page_size
    
    return templates.TemplateResponse(
        "orders.html",
        {
            "request": request,
            "restaurant_name": "Billo Restaurant",
            "orders": orders_page,
            "page": page,
            "total_pages": total_pages,
            "status": status,
            "user": user
        }
    )

# Error handlers
@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse(
        "404.html",
        {"request": request, "detail": "The requested page was not found"},
        status_code=404
    )

@app.exception_handler(500)
async def server_error_exception_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse(
        "500.html",
        {"request": request, "detail": "An internal server error occurred"},
        status_code=500
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
