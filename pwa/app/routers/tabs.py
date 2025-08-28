from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from datetime import datetime
from typing import Optional, Dict, Any

from ..auth import get_current_user, User
from ..config.business_hours import BusinessHours

router = APIRouter()

# In-memory storage (replace with database in production)
active_tabs: Dict[int, Dict[str, Any]] = {}
next_tab_number: int = 1

@router.get("/tab/new")
async def create_new_tab():
    """Create a new tab with the next available number."""
    global next_tab_number
    
    tab_id = next_tab_number
    tab = {
        "id": tab_id,
        "tab_number": tab_id,
        "status": "new",
        "created_at": datetime.now().strftime("%I:%M %p"),
        "items": [],
        "total": 0.00
    }
    
    active_tabs[tab_id] = tab
    next_tab_number += 1
    
    return {"tab_id": tab_id, "tab_number": tab_id}

@router.get("/tab/{tab_id}")
async def get_tab(tab_id: int):
    """Get tab details by ID."""
    if tab_id not in active_tabs:
        raise HTTPException(status_code=404, detail="Tab not found")
    return active_tabs[tab_id]

@router.get("/tab/scan")
async def scan_qr_code():
    """Endpoint for QR code scanning."""
    if not BusinessHours.is_open_now():
        next_open = BusinessHours.get_next_opening_time()
        next_open_str = next_open.strftime("%I:%M %p") if next_open else "later"
        return JSONResponse(
            status_code=403,
            content={
                "status": "closed",
                "message": "We're currently closed. Please come back at " + next_open_str
            }
        )
    
    # Create new tab since we're open
    tab = await create_new_tab()
    return {
        "status": "success",
        "tab_id": tab["tab_id"],
        "tab_number": tab["tab_number"],
        "redirect_url": f"/tab/{tab['tab_id']}"
    }
