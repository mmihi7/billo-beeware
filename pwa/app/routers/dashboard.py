import os
from datetime import datetime
from typing import List, Dict, Any, Optional

from fastapi import APIRouter, Request, HTTPException, status, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

from ..auth import get_current_active_user, User, oauth2_scheme
from ..config.business_hours import BusinessHours

router = APIRouter()
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "../../templates"))

# In-memory storage for active tabs (replace with database in production)
active_tabs: List[Dict[str, Any]] = [
    {"tab_number": 1, "status": "ordering", "customer": "Walk-in", "total": 45.50, "waiter": "John", "created_at": "10:30 AM"},
    {"tab_number": 2, "status": "dining", "customer": "Reservation #1234", "total": 78.25, "waiter": "Jane", "created_at": "12:15 PM"},
    {"tab_number": 3, "status": "payment_pending", "customer": "Walk-in", "total": 32.00, "waiter": "John", "created_at": "1:45 PM"}
]

# In-memory storage for waiters (replace with database in production)
WAITERS = [
    {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "+1234567890",
        "role": "Head Waiter",
        "pin": "1234",
        "image": "https://randomuser.me/api/portraits/men/32.jpg",
        "status": "available",
        "is_active": True,
        "tables": ["T1", "T2", "T3"],
        "current_orders": 3,
        "total_served": 45,
        "rating": 4.7,
        "last_active": "5 min ago",
        "lastLogin": "2 hours ago"
    },
    {
        "id": 2,
        "name": "Jane Smith",
        "email": "jane@example.com",
        "phone": "+1987654321",
        "role": "Senior Waiter",
        "pin": "2345",
        "image": "https://randomuser.me/api/portraits/women/44.jpg",
        "status": "busy",
        "is_active": True,
        "tables": ["T4", "T5"],
        "current_orders": 2,
        "total_served": 32,
        "rating": 4.9,
        "last_active": "2 min ago",
        "lastLogin": "30 min ago"
    },
    {
        "id": 3,
        "name": "Mike Johnson",
        "email": "mike@example.com",
        "phone": "+1122334455",
        "role": "Waiter",
        "pin": "3456",
        "image": "https://randomuser.me/api/portraits/men/67.jpg",
        "status": "on_break",
        "is_active": False,
        "tables": ["T6"],
        "current_orders": 0,
        "total_served": 12,
        "rating": 4.5,
        "last_active": "2 hours ago",
        "lastLogin": "1 hour ago"
    },
    {
        "id": 4,
        "name": "Sarah Williams",
        "email": "sarah@example.com",
        "phone": "+1555666777",
        "role": "Trainee",
        "pin": "4567",
        "image": "https://randomuser.me/api/portraits/women/22.jpg",
        "status": "available",
        "is_active": True,
        "tables": ["T7", "T8"],
        "current_orders": 1,
        "total_served": 28,
        "rating": 4.8,
        "last_active": "15 min ago",
        "lastLogin": "15 min ago"
    }
]

next_tab_number: int = 4

# Sample menu items
MENU_ITEMS = [
    {"name": "Margherita Pizza", "category": "Mains", "price": 12.99, "status": "available"},
    {"name": "Caesar Salad", "category": "Starters", "price": 8.99, "status": "available"},
    {"name": "Chocolate Brownie", "category": "Desserts", "price": 6.50, "status": "available"}
]

def get_dashboard_data(request, current_user, is_open, next_open):
    next_open_str = next_open.strftime("%I:%M %p") if next_open else "TBD"
    return {
        "request": request,
        "user": {
            "email": current_user.email,
            "username": getattr(current_user, 'username', current_user.email.split("@")[0])
        },
        "all_waiters": WAITERS,
        "active_tabs": active_tabs,
        "menu_items": MENU_ITEMS,
        "is_open": is_open,
        "next_open": next_open_str,
        "stats": {
            "active_tabs": len(active_tabs),
            "orders_today": 12,
            "revenue_today": 245.00,
            "pending_orders": 4
        },
        "business_hours": {
            "is_open": is_open,
            "next_open_time": next_open_str
        }
    }

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    current_user: User = Depends(get_current_active_user)
):
    """Render the main dashboard page.
    
    Args:
        request: The FastAPI request object
        current_user: The authenticated user (from dependency injection)
        
    Returns:
        Rendered dashboard template or redirect to login if not authenticated
    """
    try:
        # Check if restaurant is open
        is_open = BusinessHours.is_open_now()
        next_open = BusinessHours.get_next_opening_time()
        
        # Prepare dashboard data
        dashboard_data = get_dashboard_data(request, current_user, is_open, next_open)
        
        # Add flash messages if any
        if request.session.get("flash_message"):
            dashboard_data["flash_message"] = request.session.pop("flash_message")
        
        return templates.TemplateResponse("dashboard.html", dashboard_data)
        
    except HTTPException as e:
        if e.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN):
            # Store the current URL to redirect back after login
            request.session["next_url"] = str(request.url)
            return RedirectResponse(
                url="/login",
                status_code=status.HTTP_303_SEE_OTHER
            )
        raise
        
    except Exception as e:
        # Log the error in production
        print(f"Dashboard error: {str(e)}")
        
        # Show error page to user
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error_message": "An error occurred while loading the dashboard",
                "status_code": 500
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@router.get("/dashboard/new", response_class=HTMLResponse)
async def new_dashboard(
    request: Request,
    current_user: User = Depends(get_current_active_user)
):
    """Render the new dashboard page.
    
    This is an alternative dashboard view that can be used for testing new features.
    
    Args:
        request: The FastAPI request object
        current_user: The authenticated user (from dependency injection)
        
    Returns:
        Rendered dashboard_new.html template or redirect to login if not authenticated
    """
    try:
        # Check if restaurant is open
        is_open = BusinessHours.is_open_now()
        next_open = BusinessHours.get_next_opening_time()
        
        # Prepare dashboard data
        dashboard_data = get_dashboard_data(request, current_user, is_open, next_open)
        
        # Add flash messages if any
        if request.session.get("flash_message"):
            dashboard_data["flash_message"] = request.session.pop("flash_message")
        
        return templates.TemplateResponse("dashboard_new.html", dashboard_data)
        
    except HTTPException as e:
        if e.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN):
            # Store the current URL to redirect back after login
            request.session["next_url"] = str(request.url)
            return RedirectResponse(
                url="/login",
                status_code=status.HTTP_303_SEE_OTHER
            )
        raise
        
    except Exception as e:
        # Log the error in production
        print(f"New dashboard error: {str(e)}")
        
        # Show error page to user
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error_message": "An error occurred while loading the dashboard",
                "status_code": 500
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# Use WAITERS list instead of MOCK_WAITERS

@router.get("/waiters", response_class=HTMLResponse)
async def waiters_home(
    request: Request,
    current_user: User = Depends(get_current_active_user)
):
    """Render the waiters home page.
    
    This page shows a list of active waiters and their status.
    
    Args:
        request: The FastAPI request object
        current_user: The authenticated user (from dependency injection)
        
    Returns:
        Rendered waiters_home.html template or redirect to login if not authenticated
    """
    try:
        # Get active waiters
        active_waiters = [waiter for waiter in WAITERS if waiter.get('is_active', False)]
        
        # Prepare template context
        context = {
            "request": request,
            "user": {
                "username": getattr(current_user, 'username', current_user.email.split('@')[0]),
                "email": current_user.email,
                "is_admin": getattr(current_user, 'is_admin', False)
            },
            "waiters": active_waiters,
            "all_waiters": WAITERS
        }
        
        # Add flash messages if any
        if request.session.get("flash_message"):
            context["flash_message"] = request.session.pop("flash_message")
        
        return templates.TemplateResponse("waiters_home.html", context)
        
    except HTTPException as e:
        if e.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN):
            # Store the current URL to redirect back after login
            request.session["next_url"] = str(request.url)
            return RedirectResponse(
                url="/login",
                status_code=status.HTTP_303_SEE_OTHER
            )
        raise
        
    except Exception as e:
        # Log the error in production
        print(f"Waiters home error: {str(e)}")
        
        # Show error page to user
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error_message": "An error occurred while loading the waiters page",
                "status_code": 500
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class WaiterStatusUpdate(BaseModel):
    is_active: bool


@router.patch("/api/waiters/{waiter_id}/status")
async def update_waiter_status(
    request: Request,
    waiter_id: int,
    status_update: WaiterStatusUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """Update the active status of a waiter.
    
    Args:
        request: The FastAPI request object
        waiter_id: ID of the waiter to update
        status_update: New status data
        current_user: The authenticated user making the request
        
    Returns:
        JSON response with update status
        
    Raises:
        HTTPException: If waiter not found or user not authorized
    """
    try:
        # Check if user has permission to update waiter status
        if not getattr(current_user, 'is_admin', False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin users can update waiter status"
            )
        
        # Find the waiter by ID
        waiter = next((w for w in WAITERS if w["id"] == waiter_id), None)
        if not waiter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Waiter with ID {waiter_id} not found"
            )
        
        # Update the status
        previous_status = waiter.get("is_active", False)
        waiter["is_active"] = status_update.is_active
        
        # In a real app, you would update this in the database here
        # db.update_waiter_status(waiter_id, status_update.is_active)
        
        # Log the status change
        print(f"Waiter {waiter_id} status changed from {previous_status} to {status_update.is_active} by {current_user.email}")
        
        # Add a flash message for the next request
        request.session["flash_message"] = {
            "type": "success",
            "message": f"Successfully updated waiter {waiter_id} status"
        }
        
        return {
            "status": "success",
            "message": f"Waiter {waiter_id} status updated successfully",
            "data": {
                "waiter_id": waiter_id,
                "is_active": status_update.is_active,
                "updated_at": datetime.utcnow().isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        # Log the error in production
        print(f"Error updating waiter status: {str(e)}")
        
        # Return error response
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating waiter status"
        )

@router.get("/waiter-dashboard/{waiter_id}", response_class=HTMLResponse)
async def waiter_dashboard(
    request: Request, 
    waiter_id: int, 
    current_user: User = Depends(get_current_active_user)
):
    """Render the waiter's personal dashboard.
    
    This page shows the waiter's active orders, status, and other relevant information.
    """
    try:
        # Find the requested waiter from the WAITERS list
        waiter = next((w for w in WAITERS if w["id"] == waiter_id), None)
        if not waiter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Waiter with ID {waiter_id} not found"
            )
            
        # Check if the current user is authorized to view this waiter's dashboard
        is_authorized = (
            getattr(current_user, 'is_admin', False) or  # Admin can view any waiter
            str(waiter_id) == getattr(current_user, 'waiter_id', '') or  # Or it's their own dashboard
            current_user.email == waiter.get('email')  # Or it's their own email
        )
        
        if not is_authorized:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this waiter's dashboard"
            )
            
        # Get active orders for this waiter
        active_orders = [
            {
                "id": 100 + i,
                "table": table,
                "items": ["Pizza Margherita", "Coke"] if i % 2 == 0 else ["Pasta Carbonara", "Wine"],
                "total": 25.99 if i % 2 == 0 else 32.50,
                "status": "preparing" if i % 2 == 0 else "ready",
                "time_elapsed": f"{15 + (i*5)}m"
            }
            for i, table in enumerate(waiter.get('tables', [])[:3])  # Max 3 orders for demo
        ]
        
        # Calculate waiter statistics
        stats = {
            "tables_served": len(waiter.get('tables', [])),
            "active_orders": len(active_orders),
            "total_earnings": sum(order["total"] for order in active_orders),
            "rating": waiter.get('rating', 4.5)
        }
        
        # Prepare template context
        context = {
            "request": request,
            "waiter": {
                "id": waiter["id"],
                "name": waiter["name"],
                "email": waiter["email"],
                "phone": waiter["phone"],
                "role": waiter["role"],
                "status": waiter["status"],
                "image": waiter.get("image", ""),
                "last_active": waiter["last_active"],
                "tables": waiter.get("tables", [])
            },
            "active_orders": active_orders,
            "stats": stats,
            "current_time": datetime.now().strftime("%H:%M"),
            "user": {
                "username": getattr(current_user, 'username', current_user.email.split('@')[0]),
                "email": current_user.email,
                "is_admin": getattr(current_user, 'is_admin', False)
            }
        }
        
        # Add flash messages if any
        if request.session.get("flash_message"):
            context["flash_message"] = request.session.pop("flash_message")
            
        return templates.TemplateResponse("waiter_dashboard.html", context)
        
    except HTTPException as e:
        if e.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN):
            # Store the current URL to redirect back after login
            request.session["next_url"] = str(request.url)
            return RedirectResponse(
                url="/login",
                status_code=status.HTTP_303_SEE_OTHER
            )
        raise
        
    except Exception as e:
        # Log the error in production
        print(f"Waiter dashboard error: {str(e)}")
        
        # Show error page to user
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error_message": "An error occurred while loading the waiter dashboard",
                "status_code": 500
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
