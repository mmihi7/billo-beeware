from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from datetime import time
from typing import Dict, List, Optional
import json
import os
from pathlib import Path

from ..auth import get_current_user

router = APIRouter()

# Path to store business hours
BUSINESS_HOURS_FILE = Path(__file__).parent.parent / "data" / "business_hours.json"

# Ensure data directory exists
BUSINESS_HOURS_FILE.parent.mkdir(parents=True, exist_ok=True)

# Default business hours
DEFAULT_BUSINESS_HOURS = {
    "monday": ["09:00", "22:00"],
    "tuesday": ["09:00", "22:00"],
    "wednesday": ["09:00", "22:00"],
    "thursday": ["09:00", "22:00"],
    "friday": ["09:00", "23:00"],
    "saturday": ["10:00", "23:00"],
    "sunday": ["10:00", "21:00"]
}

def load_business_hours() -> Dict[str, List[Optional[str]]]:
    """Load business hours from file or return default if file doesn't exist."""
    try:
        if BUSINESS_HOURS_FILE.exists():
            with open(BUSINESS_HOURS_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading business hours: {e}")
    
    # Return default if file doesn't exist or there's an error
    return DEFAULT_BUSINESS_HOURS

def save_business_hours(hours: Dict[str, List[Optional[str]]]) -> None:
    """Save business hours to file."""
    try:
        with open(BUSINESS_HOURS_FILE, 'w') as f:
            json.dump(hours, f, indent=2)
    except Exception as e:
        print(f"Error saving business hours: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save business hours"
        )

@router.get("/api/business-hours", response_model=Dict[str, List[Optional[str]]])
async def get_business_hours():
    """Get current business hours."""
    return load_business_hours()

@router.post("/api/business-hours")
async def update_business_hours(hours: Dict[str, List[Optional[str]]], current_user = Depends(get_current_user)):
    """Update business hours."""
    # Validate the input
    valid_days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    
    for day in hours:
        if day not in valid_days:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid day: {day}. Must be one of {valid_days}"
            )
            
        day_hours = hours[day]
        if day_hours is not None:
            if not isinstance(day_hours, list) or len(day_hours) != 2:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid hours format for {day}. Expected [open_time, close_time]"
                )
    
    # Save the updated hours
    save_business_hours(hours)
    return {"status": "success", "message": "Business hours updated successfully"}
