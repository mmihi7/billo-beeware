from datetime import time, datetime
from typing import Dict, Optional
from pydantic import BaseModel

class BusinessHours(BaseModel):
    """Business hours configuration for the restaurant."""
    monday: tuple[time, time] = (time(9, 0), time(22, 0))  # (open, close)
    tuesday: tuple[time, time] = (time(9, 0), time(22, 0))
    wednesday: tuple[time, time] = (time(9, 0), time(22, 0))
    thursday: tuple[time, time] = (time(9, 0), time(22, 0))
    friday: tuple[time, time] = (time(9, 0), time(23, 0))
    saturday: tuple[time, time] = (time(10, 0), time(23, 0))
    sunday: tuple[time, time] = (time(10, 0), time(21, 0))

    @classmethod
    def is_open_now(cls) -> bool:
        """Check if the restaurant is currently open based on business hours."""
        now = datetime.now().time()
        today = datetime.today().strftime('%A').lower()
        
        # Get today's hours (default to closed if not found)
        hours = getattr(cls(), today, (None, None))
        if not all(isinstance(t, time) for t in hours):
            return False
            
        open_time, close_time = hours
        return open_time <= now <= close_time

    @classmethod
    def get_next_opening_time(cls) -> Optional[time]:
        """Get the next time the restaurant will be open."""
        today = datetime.today()
        current_time = today.time()
        current_weekday = today.strftime('%A').lower()
        
        # Check remaining time today
        hours = getattr(cls(), current_weekday, (None, None))
        if all(isinstance(t, time) for t in hours):
            open_time, close_time = hours
            if current_time < close_time:
                return close_time
        
        # Find next open day
        weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        current_idx = weekdays.index(current_weekday)
        
        for i in range(1, 8):  # Check next 7 days
            next_day = weekdays[(current_idx + i) % 7]
            hours = getattr(cls(), next_day, (None, None))
            if all(isinstance(t, time) for t in hours):
                return hours[0]  # Return opening time of next open day
                
        return None
