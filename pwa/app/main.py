from fastapi import FastAPI, Request, Depends, Form, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.sessions import SessionMiddleware
from datetime import timedelta
import os
import secrets

# Import routers and auth
from .routers import dashboard, business_hours
from .auth import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

def create_app():
    app = FastAPI()
    
    # Add session middleware
    app.add_middleware(
        SessionMiddleware,
        secret_key=os.getenv("SECRET_KEY", secrets.token_hex(32)),
        session_cookie="billo_session",
        max_age=3600  # 1 hour
    )
    
    # Add trusted host middleware for security
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"],  # In production, replace with your domain
    )
    
    # Set up templates
    templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "../templates"))
    
    # Mount static files
    app.mount(
        "/static",
        StaticFiles(directory=os.path.join(os.path.dirname(__file__), "../static")),
        name="static"
    )
    
    # Include routers
    app.include_router(dashboard.router)
    app.include_router(business_hours.router)
    
    @app.get("/", response_class=HTMLResponse)
    async def home(request: Request):
        return RedirectResponse(url="/login")
    
    # Login page
    @app.get("/login", response_class=HTMLResponse)
    async def login_page(request: Request, error: str = None):
        return templates.TemplateResponse("login_simple.html", {
            "request": request,
            "error": error
        })
    
    # Process login form
    @app.post("/login")
    async def login(
        request: Request,
        username: str = Form(...),
        password: str = Form(...)
    ):
        try:
            # Validate input
            if not username or not password:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email and password are required"
                )
            
            # Authenticate user
            user = authenticate_user(username, password)
            if not user:
                return templates.TemplateResponse(
                    "login_simple.html",
                    {
                        "request": request,
                        "error": "Incorrect email or password"
                    },
                    status_code=status.HTTP_401_UNAUTHORIZED
                )
            
            # Check if user is active
            if hasattr(user, 'disabled') and user.disabled:
                return templates.TemplateResponse(
                    "login_simple.html",
                    {
                        "request": request,
                        "error": "This account has been deactivated"
                    },
                    status_code=status.HTTP_403_FORBIDDEN
                )
            
            # Store minimal user info in session
            request.session["user"] = {
                "email": user.email,
                "username": getattr(user, 'username', user.email.split('@')[0]),
                "is_authenticated": True
            }
            
            # Set session timeout (1 hour)
            request.session.set_expiry(3600)
            
            # Redirect to dashboard or next URL
            next_url = request.query_params.get("next", "/dashboard")
            return RedirectResponse(
                url=next_url,
                status_code=status.HTTP_303_SEE_OTHER
            )
            
        except HTTPException:
            raise
        except Exception as e:
            # Log the error in production
            print(f"Login error: {str(e)}")
            return templates.TemplateResponse(
                "login_simple.html",
                {
                    "request": request,
                    "error": "An error occurred during login. Please try again."
                },
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    # Logout
    @app.get("/logout")
    @app.post("/logout")
    async def logout(request: Request):
        # Clear the session
        request.session.clear()
        response = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
        # Clear any cookies
        response.delete_cookie("session")
        return response
    
    return app

app = create_app()

def main():
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()
