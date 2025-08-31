from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from pydantic import BaseModel
from datetime import datetime
from app.core.jwt import get_current_user

router = APIRouter(prefix="/restaurant", tags=["restaurant"])

class MenuItemCreate(BaseModel):
    name: str
    description: str
    price: int  # in cents
    category: str
    is_available: bool = True
    image_url: Optional[str] = None

class MenuItem(MenuItemCreate):
    id: str
    restaurant_id: str
    created_at: datetime
    updated_at: datetime

class WaiterCreate(BaseModel):
    email: str
    full_name: str
    phone: str
    pin: str  # 4-6 digit PIN for waiter login

class Waiter(WaiterCreate):
    id: str
    restaurant_id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

@router.post("/menu/items", response_model=MenuItem)
async def create_menu_item(
    item: MenuItemCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Add a new menu item (Restaurant admin only)
    """
    if current_user["role"] != "restaurant_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only restaurant admins can add menu items"
        )
    
    # TODO: Implement menu item creation with Supabase
    # This is a placeholder implementation
    new_item = {
        **item.dict(),
        "id": "item_123",  # Generate UUID in actual implementation
        "restaurant_id": current_user["restaurant_id"],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    return new_item

@router.get("/menu/items", response_model=List[MenuItem])
async def get_menu_items(
    category: str = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Get all menu items for the restaurant
    """
    # TODO: Implement menu item retrieval from Supabase
    # Filter by category if provided
    return []

@router.post("/waiters", response_model=Waiter)
async def create_waiter(
    waiter: WaiterCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Add a new waiter (Restaurant admin only)
    """
    if current_user["role"] != "restaurant_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only restaurant admins can add waiters"
        )
    
    # TODO: Implement waiter creation with Supabase
    # This is a placeholder implementation
    new_waiter = {
        **waiter.dict(),
        "id": "waiter_123",  # Generate UUID in actual implementation
        "restaurant_id": current_user["restaurant_id"],
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    return new_waiter

@router.get("/waiters", response_model=List[Waiter])
async def get_waiters(
    active_only: bool = True,
    current_user: dict = Depends(get_current_user)
):
    """
    Get all waiters for the restaurant
    """
    # TODO: Implement waiter retrieval from Supabase
    # Filter by active status if active_only is True
    return []
