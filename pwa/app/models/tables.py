from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum

class TabStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PAID = "paid"
    CANCELLED = "cancelled"

class OrderStatus(str, Enum):
    PLACED = "placed"
    PREPARING = "preparing"
    READY = "ready"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class OrderItemBase(BaseModel):
    menu_item_id: int
    name: str
    quantity: int = Field(..., gt=0)
    price: float = Field(..., gt=0)
    notes: Optional[str] = None

class OrderItemCreate(OrderItemBase):
    pass

class OrderItem(OrderItemBase):
    id: int
    order_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class OrderBase(BaseModel):
    tab_id: int
    status: OrderStatus = OrderStatus.PLACED
    customer_name: Optional[str] = None
    special_instructions: Optional[str] = None

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

class Order(OrderBase):
    id: int
    created_at: datetime
    updated_at: datetime
    items: List[OrderItem] = []

    class Config:
        orm_mode = True

class TabBase(BaseModel):
    number: str
    status: TabStatus = TabStatus.ACTIVE
    customer_name: Optional[str] = None
    waiter_id: Optional[int] = None

class TabCreate(TabBase):
    pass

class Tab(TabBase):
    id: int
    created_at: datetime
    updated_at: datetime
    orders: List[Order] = []
    total: float = 0.0

    class Config:
        orm_mode = True
