from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from .base import BaseDBModel

# Enums
class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class PaymentMethod(str, Enum):
    CASH = "cash"
    CARD = "card"
    MOBILE_MONEY = "mobile_money"
    OTHER = "other"

class TabStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"
    PAID = "paid"
    OVERDUE = "overdue"

# Models
class OrderItem(BaseModel):
    """Represents an item in an order"""
    menu_item_id: str
    name: str
    quantity: int = Field(gt=0)
    unit_price: float = Field(gt=0)
    special_instructions: Optional[str] = None
    total_price: float = Field(gt=0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "menu_item_id": "item_123",
                "name": "Margherita Pizza",
                "quantity": 2,
                "unit_price": 12.99,
                "special_instructions": "No basil, extra cheese",
                "total_price": 25.98
            }
        }

class OrderBase(BaseDBModel):
    """Base order model"""
    restaurant_id: str
    table_number: Optional[str] = None
    customer_id: Optional[str] = None
    status: OrderStatus = OrderStatus.PENDING
    items: List[OrderItem] = []
    subtotal: float = Field(ge=0)
    tax: float = Field(ge=0)
    discount: float = Field(ge=0)
    total: float = Field(ge=0)
    notes: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "order_123",
                "restaurant_id": "rest_456",
                "table_number": "A1",
                "status": "pending",
                "subtotal": 25.98,
                "tax": 2.60,
                "discount": 0.0,
                "total": 28.58,
                "created_at": "2023-01-01T12:00:00Z"
            }
        }

class OrderCreate(BaseModel):
    """Schema for creating a new order"""
    restaurant_id: str
    table_number: Optional[str] = None
    items: List[OrderItem]
    customer_id: Optional[str] = None
    notes: Optional[str] = None

class OrderUpdate(BaseModel):
    """Schema for updating an order"""
    status: Optional[OrderStatus] = None
    items: Optional[List[OrderItem]] = None
    notes: Optional[str] = None

class PaymentBase(BaseDBModel):
    """Base payment model"""
    order_id: str
    amount: float = Field(gt=0)
    currency: str = "KES"
    status: PaymentStatus = PaymentStatus.PENDING
    method: PaymentMethod
    transaction_id: Optional[str] = None
    notes: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "pay_123",
                "order_id": "order_123",
                "amount": 28.58,
                "currency": "KES",
                "status": "completed",
                "method": "mobile_money",
                "transaction_id": "mpesa_123456",
                "created_at": "2023-01-01T12:05:00Z"
            }
        }

class PaymentCreate(BaseModel):
    """Schema for creating a payment"""
    order_id: str
    amount: float = Field(gt=0)
    method: PaymentMethod
    transaction_id: Optional[str] = None
    notes: Optional[str] = None

class TabBase(BaseDBModel):
    """Base tab model for tracking customer tabs"""
    restaurant_id: str
    customer_id: str
    table_number: Optional[str] = None
    status: TabStatus = TabStatus.OPEN
    subtotal: float = Field(ge=0)
    tax: float = Field(ge=0)
    discount: float = Field(ge=0)
    total: float = Field(ge=0)
    paid_amount: float = Field(ge=0)
    balance: float = Field(ge=0)
    notes: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "tab_123",
                "restaurant_id": "rest_456",
                "customer_id": "cust_789",
                "table_number": "B2",
                "status": "open",
                "subtotal": 150.0,
                "tax": 15.75,
                "discount": 0.0,
                "total": 165.75,
                "paid_amount": 100.0,
                "balance": 65.75,
                "created_at": "2023-01-01T18:00:00Z"
            }
        }

class TabCreate(BaseModel):
    """Schema for creating a new tab"""
    restaurant_id: str
    customer_id: str
    table_number: Optional[str] = None
    notes: Optional[str] = None

class TabUpdate(BaseModel):
    """Schema for updating a tab"""
    status: Optional[TabStatus] = None
    notes: Optional[str] = None

# Response Models
class OrderResponse(OrderBase):
    """Order response with related data"""
    payments: List[PaymentBase] = []

class TabResponse(TabBase):
    """Tab response with related orders and payments"""
    orders: List[OrderBase] = []
    payments: List[PaymentBase] = []
