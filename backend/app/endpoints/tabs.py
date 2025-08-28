from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime, date, time
from app.models.schemas import Tab, TabCreate, TabStatus, OrderStatus
from app.core.database import supabase
from pydantic import BaseModel

class QRCodeData(BaseModel):
    restaurant_id: str
    table_number: Optional[str] = None  # For reference only, not used in logic

router = APIRouter()

@router.post("/", response_model=Tab, status_code=status.HTTP_201_CREATED)
async def create_tab(tab_create: TabCreate):
    """Create a new tab with sequential number for the day"""
    try:
        # Get current date
        today = date.today()
        
        # Get max tab number for today
        result = supabase.table("tabs").select("tab_number").eq("restaurant_id", tab_create.restaurant_id).eq("created_at::date", today.isoformat()).order("tab_number", desc=True).limit(1).execute()
        
        # Calculate next tab number
        next_tab_number = 1
        if result.data:
            next_tab_number = result.data[0]["tab_number"] + 1
        
        # Create tab
        tab_data = {
            **tab_create.dict(),
            "tab_number": next_tab_number,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        result = supabase.table("tabs").insert(tab_data).execute()
        return result.data[0]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create tab: {str(e)}"
        )

@router.post("/scan", response_model=Tab, status_code=status.HTTP_201_CREATED)
async def scan_qr_code(qr_data: QRCodeData):
    """
    Handle QR code scan from customer
    - Validates restaurant is open
    - Creates a new tab with next sequential number
    - Returns tab details for customer
    """
    try:
        # 1. Check if restaurant exists and get business hours
        restaurant = supabase.table("restaurants").select("*").eq("id", qr_data.restaurant_id).execute()
        if not restaurant.data:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        
        restaurant = restaurant.data[0]
        
        # 2. Check if restaurant is open (simplified check)
        current_time = datetime.utcnow().time()
        open_time = time(8, 0)  # Default 8 AM
        close_time = time(22, 0)  # Default 10 PM
        
        if current_time < open_time or current_time > close_time:
            raise HTTPException(
                status_code=400,
                detail=f"Restaurant is currently closed. Open hours: {open_time.strftime('%H:%M')} - {close_time.strftime('%H:%M')}"
            )
        
        # 3. Generate next tab number
        today = date.today()
        result = supabase.table("tabs") \
            .select("tab_number") \
            .eq("restaurant_id", qr_data.restaurant_id) \
            .eq("created_at::date", today.isoformat()) \
            .order("tab_number", desc=True) \
            .limit(1) \
            .execute()
        
        next_tab_number = 1
        if result.data:
            next_tab_number = result.data[0]["tab_number"] + 1
        
        # 4. Create new tab
        tab_data = {
            "restaurant_id": qr_data.restaurant_id,
            "status": TabStatus.INACTIVE,
            "tab_number": next_tab_number,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "reference": f"TAB-{today.strftime('%Y%m%d')}-{next_tab_number:03d}"
        }
        
        result = supabase.table("tabs").insert(tab_data).execute()
        return result.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process QR code: {str(e)}")

@router.get("/{tab_id}", response_model=Tab)
async def get_tab(tab_id: str):
    """Get a specific tab by ID"""
    try:
        result = supabase.table("tabs").select("*").eq("id", tab_id).execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Tab not found")
        return result.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/restaurant/{restaurant_id}", response_model=List[Tab])
async def get_restaurant_tabs(restaurant_id: str, status: Optional[TabStatus] = None):
    """Get all tabs for a restaurant, optionally filtered by status"""
    try:
        query = supabase.table("tabs").select("*").eq("restaurant_id", restaurant_id)
        if status:
            query = query.eq("status", status.value)
        result = query.order("created_at", desc=True).execute()
        return result.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))