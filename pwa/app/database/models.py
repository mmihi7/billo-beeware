from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, date
from typing import List, Optional
import enum

from .base import Base

# Enums for status fields
class TabStatus(str, enum.Enum):
    INACTIVE = "inactive"
    ACTIVE = "active"
    PAYMENT_PENDING = "payment_pending"
    PAID = "paid"
    CANCELLED = "cancelled"

class OrderStatus(str, enum.Enum):
    PLACED = "placed"
    PREPARING = "preparing"
    READY = "ready"
    DELIVERED = "delivered"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    CONFIRMED = "confirmed"
    FAILED = "failed"

class PaymentMethod(str, enum.Enum):
    CASH = "cash"
    MOBILE_MONEY = "mobile_money"
    CARD = "card"
    OTHER = "other"

# Association tables for many-to-many relationships
order_waiter = Table(
    'order_waiter',
    Base.metadata,
    Column('order_id', Integer, ForeignKey('orders.id'), primary_key=True),
    Column('waiter_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('assigned_at', DateTime(timezone=True), server_default=func.now())
)

class User(Base):
    __tablename__ = 'users'
    
    id = Column(String, primary_key=True)  # Supabase auth ID
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String)
    phone_number = Column(String)
    role = Column(String)  # 'admin', 'waiter', 'chef', etc.
    pin_hash = Column(String)  # For waiter PIN authentication (hashed)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    assigned_orders = relationship("Order", secondary=order_waiter, back_populates="waiters")
    
class Restaurant(Base):
    __tablename__ = 'restaurants'
    
    id = Column(String, primary_key=True)  # Supabase auth ID for the restaurant
    name = Column(String, nullable=False)
    address = Column(Text)
    phone_number = Column(String)
    logo_url = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    tabs = relationship("Tab", back_populates="restaurant")
    menu_items = relationship("MenuItem", back_populates="restaurant")

class Tab(Base):
    __tablename__ = 'tabs'
    
    id = Column(String, primary_key=True)  # UUID
    restaurant_id = Column(String, ForeignKey('restaurants.id'), nullable=False)
    number = Column(String(10), index=True, nullable=False)  # e.g., "T-001"
    status = Column(Enum(TabStatus), default=TabStatus.INACTIVE, nullable=False)
    customer_name = Column(String(100))
    customer_phone = Column(String(20))
    customer_email = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    closed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    restaurant = relationship("Restaurant", back_populates="tabs")
    orders = relationship("Order", back_populates="tab", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="tab", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="tab", cascade="all, delete-orphan")
    
    @property
    def total_amount(self) -> float:
        """Total amount for all orders in this tab"""
        return sum(order.total_amount for order in self.orders)
    
    @property
    def amount_paid(self) -> float:
        """Total amount paid for this tab"""
        return sum(payment.amount for payment in self.payments 
                  if payment.status == PaymentStatus.CONFIRMED)
    
    @property
    def balance(self) -> float:
        """Remaining balance for this tab"""
        return self.total_amount - self.amount_paid

class Order(Base):
    __tablename__ = 'orders'
    
    id = Column(String, primary_key=True)  # UUID
    tab_id = Column(String, ForeignKey('tabs.id'), nullable=False, index=True)
    status = Column(Enum(OrderStatus), default=OrderStatus.PLACED, nullable=False)
    special_instructions = Column(Text)
    placed_at = Column(DateTime(timezone=True), server_default=func.now())
    prepared_at = Column(DateTime(timezone=True), nullable=True)
    ready_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    tab = relationship("Tab", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    waiters = relationship("User", secondary=order_waiter, back_populates="assigned_orders")
    
    @property
    def total_amount(self) -> float:
        """Total amount for this order (sum of all items)"""
        return sum(item.price * item.quantity for item in self.items)

class OrderItem(Base):
    __tablename__ = 'order_items'
    
    id = Column(String, primary_key=True)  # UUID
    order_id = Column(String, ForeignKey('orders.id'), nullable=False, index=True)
    menu_item_id = Column(String, nullable=False, index=True)  # Reference to menu item
    name = Column(String(100), nullable=False)
    description = Column(Text)
    quantity = Column(Integer, nullable=False, default=1)
    price = Column(Float, nullable=False)  # Price at time of ordering
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    order = relationship("Order", back_populates="items")

class Payment(Base):
    __tablename__ = 'payments'
    
    id = Column(String, primary_key=True)  # UUID
    tab_id = Column(String, ForeignKey('tabs.id'), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="KES", nullable=False)
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    reference = Column(String)  # External reference (e.g., M-Pesa code)
    processed_by = Column(String, ForeignKey('users.id'))
    processed_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    failure_reason = Column(Text)
    
    # Relationships
    tab = relationship("Tab", back_populates="payments")
    processor = relationship("User")

class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(String, primary_key=True)  # UUID
    tab_id = Column(String, ForeignKey('tabs.id'), nullable=False, index=True)
    sender_id = Column(String, ForeignKey('users.id'))
    sender_type = Column(String)  # 'customer', 'waiter', 'system'
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    tab = relationship("Tab", back_populates="messages")
    sender = relationship("User")

# Menu models (simplified - could be in a separate file)
class MenuItem(Base):
    __tablename__ = 'menu_items'
    
    id = Column(String, primary_key=True)  # UUID
    restaurant_id = Column(String, ForeignKey('restaurants.id'), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    category = Column(String(50), nullable=False)
    is_available = Column(Boolean, default=True)
    image_url = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    restaurant = relationship("Restaurant", back_populates="menu_items")
