from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum

class TabStatus(str, Enum):
    INACTIVE = "inactive"
    ACTIVE = "active"
    PAYMENT_PENDING = "payment_pending"
    PAID = "paid"
    CANCELLED = "cancelled"

class OrderStatus(str, Enum):
    PLACED = "placed"
    PREPARING = "preparing"
    READY = "ready"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class PaymentMethod(str, Enum):
    CASH = "cash"
    MOBILE_MONEY = "mobile_money"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    CONFIRMED = "confirmed"
    FAILED = "failed"

class TabBase(BaseModel):
    restaurant_id: str = Field(..., description="Restaurant ID")
    customer_id: Optional[str] = Field(None, description="Customer ID")
    status: TabStatus = Field(TabStatus.INACTIVE, description="Tab status")

class TabCreate(TabBase):
    pass

class Tab(TabBase):
    id: str
    tab_number: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class OrderItem(BaseModel):
    menu_item_id: str
    name: str
    price: int  # in cents
    quantity: int

class OrderCreate(BaseModel):
    tab_id: str
    waiter_id: str
    items: List[OrderItem]

class Order(OrderCreate):
    id: str
    status: OrderStatus = OrderStatus.PLACED
    total: int
    created_at: datetime
    updated_at: datetime

class PaymentCreate(BaseModel):
    tab_id: str
    amount: int
    method: PaymentMethod
    phone_number: Optional[str] = None

class Payment(PaymentCreate):
    id: str
    status: PaymentStatus = PaymentStatus.PENDING
    created_at: datetime