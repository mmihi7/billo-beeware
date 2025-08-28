---
trigger: model_decision
description: Enforces Python-first development, BeeWare Android app, Python PWA for restaurants, strict data models, onboarding flows, WSL+Poetry+Briefcase builds, backend-driven state machines, and mandatory ask-first discipline.
---

# BILL0 LLM RULEBOOK — **Version: Updated (Two Clients, Python PWA, BeeWare Android)**

*Badass, enforceable rules to keep the LLM honest — full data models, onboarding flows, build rules (WSL), and “no JS/TS” for PWA. Python-first. BeeWare/Briefcase for Android. Read these before you touch anything.*

---


# 1) Why this update

You specified two clients and *no JS/TS for the PWA*. This file updates the original rulebook to:

* Make **Restaurant** client a **Python PWA** (no React, no JS/TS).
* Make **Customer** client a **BeeWare Android** app (Toga/Briefcase).
* Provide **complete data models** (tabs, waiters, orders, messages, menu\_items, payments, users).
* Provide onboarding flow steps and UI behavior (welcome → terms → signup → home → connect → bills/chat).
* Preserve backend-first, Python-first, and mobile packaging constraints from the canonical docs.  &#x20;

---

# 2) Product surface (two clients)

* **Restaurant (Operator)**

  * **Type:** Python PWA (must be implemented using Python web frameworks / Python-based front-end techniques — no React/JS/TS).
  * **Primary purpose:** Manage tabs, accept/confirm orders, view realtime messages, mark payments.

* **Customer (Patron)**

  * **Type:** Android native app packaged with **BeeWare/Briefcase** (Toga GUI).
  * **Primary purpose:** Connect to restaurant, place orders, chat with waiter, view bills, pay.

**Backend**: FastAPI (Python) with centralized business logic and all domain state. Clients are thin.&#x20;

---

# 3) Canonical product docs (read-first — every time)

Before changing anything, load and align to these docs (the canonical truth):

* `business-logic.md` — core business rules & state machines.&#x20;
* `mobile-structure.md` — mobile repo structure and canonical file tree.&#x20;
* `environment-setup.md` — Poetry + Briefcase instructions and WSL guidance.&#x20;

If your change conflicts with any definitive rule in those files, **stop** and ask clarifying blocking questions.

---

# 4) Full Data Models (Python-first)

Below are canonical models. Use **SQLAlchemy** for DB models and **Pydantic** for request/response schemas. These models are intentionally explicit — use them as the single source for migrations, endpoints, and client DTOs.

> Implementation notes:
>
> * Money fields: `int` cents (no floats).&#x20;
> * Tab numbers: unique per `(restaurant_id, date, tab_number)` enforced at DB level.&#x20;
> * Snapshot menu prices stored on order items.&#x20;

---

## 4.1 SQLAlchemy (ORM) — canonical models (simplified)

```py
# billo-backend/app/models/base.py
from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
# use created_at/updated_at standardized columns
```

```py
# billo-backend/app/models/restaurant.py
from sqlalchemy import Column, Integer, String, Boolean, Text
from sqlalchemy.orm import relationship
from .base import Base

class Restaurant(Base):
    __tablename__ = "restaurants"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False)
    address = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    # relationships
    menu_items = relationship("MenuItem", back_populates="restaurant")
    tabs = relationship("Tab", back_populates="restaurant")
```

```py
# billo-backend/app/models/menu_item.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class MenuItem(Base):
    __tablename__ = "menu_items"
    id = Column(Integer, primary_key=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price_cents = Column(Integer, nullable=False)  # price snapshot default when used in orders
    is_active = Column(Boolean, default=True)
    restaurant = relationship("Restaurant", back_populates="menu_items")
```

```py
# billo-backend/app/models/user.py
from sqlalchemy import Column, Integer, String, Text, Boolean
from .base import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(320), unique=True, nullable=True)  # customers may register via Supabase
    phone = Column(String(32), unique=True, nullable=True)
    name = Column(String(255), nullable=True)
    role = Column(String(32), default="customer")  # values: customer, admin
    # use Supabase JWT for auth for customers; store only minimal mirrored record if desired
```

```py
# billo-backend/app/models/waiter.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Waiter(Base):
    __tablename__ = "waiters"
    id = Column(Integer, primary_key=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    name = Column(String(255), nullable=False)
    pin_hash = Column(String(512), nullable=False)  # salted+argon2id or bcrypt
    # relationship
    restaurant = relationship("Restaurant")
```

```py
# billo-backend/app/models/tab.py
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Enum
from sqlalchemy.orm import relationship
from .base import Base
import enum

class TabStatus(str, enum.Enum):
    inactive = "inactive"
    active = "active"
    payment_pending = "payment_pending"
    paid = "paid"
    cancelled = "cancelled"

class Tab(Base):
    __tablename__ = "tabs"
    id = Column(Integer, primary_key=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    tab_number = Column(Integer, nullable=False)
    date = Column(Date, nullable=False)  # date the tab belongs to (for reset)
    status = Column(Enum(TabStatus), default=TabStatus.inactive, nullable=False)
    waiter_id = Column(Integer, ForeignKey("waiters.id"), nullable=True)
    total_cents = Column(Integer, default=0, nullable=False)
    # relationships
    restaurant = relationship("Restaurant", back_populates="tabs")
    orders = relationship("Order", back_populates="tab")
    messages = relationship("Message", back_populates="tab")
    payments = relationship("Payment", back_populates="tab")
    __table_args__ = (
        # Unique constraint for (restaurant_id, date, tab_number)
    )
```

```py
# billo-backend/app/models/order.py
from sqlalchemy import Column, Integer, ForeignKey, Enum, DateTime, JSON
from sqlalchemy.orm import relationship
from .base import Base
import enum

class OrderStatus(str, enum.Enum):
    placed = "placed"
    preparing = "preparing"
    ready = "ready"
    delivered = "delivered"
    completed = "completed"

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    tab_id = Column(Integer, ForeignKey("tabs.id"), nullable=False)
    waiter_id = Column(Integer, ForeignKey("waiters.id"), nullable=True)
    status = Column(Enum(OrderStatus), default=OrderStatus.placed, nullable=False)
    placed_at = Column(DateTime(timezone=True), server_default=func.now())
    # snapshot items: list of {menu_item_id, name, price_cents, qty}
    snapshot_items = Column(JSON, nullable=False)
    subtotal_cents = Column(Integer, nullable=False)
    tax_cents = Column(Integer, default=0, nullable=False)
    total_cents = Column(Integer, nullable=False)
    tab = relationship("Tab", back_populates="orders")
```

```py
# billo-backend/app/models/payment.py
from sqlalchemy import Column, Integer, ForeignKey, String, Enum, DateTime, JSON
from sqlalchemy.orm import relationship
from .base import Base
import enum

class PaymentStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    confirmed = "confirmed"
    failed = "failed"

class PaymentMethod(str, enum.Enum):
    cash = "cash"
    mobile_money = "mobile_money"

class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True)
    tab_id = Column(Integer, ForeignKey("tabs.id"), nullable=False)
    method = Column(Enum(PaymentMethod), nullable=False)
    provider_meta = Column(JSON, nullable=True)  # store webhook payloads, provider ids
    status = Column(Enum(PaymentStatus), default=PaymentStatus.pending, nullable=False)
    amount_cents = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    tab = relationship("Tab", back_populates="payments")
```

```py
# billo-backend/app/models/message.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from .base import Base

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    tab_id = Column(Integer, ForeignKey("tabs.id"), nullable=False)
    sender_type = Column(String(32), nullable=False)  # waiter, customer, system
    sender_id = Column(Integer, nullable=True)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    tab = relationship("Tab", back_populates="messages")
```

---

## 4.2 Pydantic schemas (examples)

```py
# billo-backend/app/schemas/tab.py
from pydantic import BaseModel
from typing import List
from datetime import date

class TabCreate(BaseModel):
    restaurant_id: int
    waiter_id: int | None = None

class TabOut(BaseModel):
    id: int
    tab_number: int
    status: str
    total_cents: int
    date: date
    class Config:
        orm_mode = True
```
```py
# billo-backend/app/schemas/order.py
from pydantic import BaseModel, Field, validator, root_validator
from typing import List, Literal
from datetime import datetime

class OrderItem(BaseModel):
    menu_item_id: int
    name: str
    price_cents: int = Field(..., ge=0)
    qty: int = Field(..., gt=0)

class OrderCreate(BaseModel):
    tab_id: int
    waiter_id: int | None = None
    items: List[OrderItem]
    note: str | None = None  # optional customer/waiter note

    @validator("items")
    def items_must_not_be_empty(cls, v):
        if not v:
            raise ValueError("order must contain at least one item")
        return v

    @root_validator
    def compute_totals_snapshot(cls, values):
        # Note: actual computation should be done server-side to prevent tampering.
        # This validator only sanity-checks item fields.
        items = values.get("items", [])
        subtotal = sum(it.price_cents * it.qty for it in items)
        values.setdefault("subtotal_cents", subtotal)
        return values

class OrderOut(BaseModel):
    id: int
    tab_id: int
    waiter_id: int | None
    status: str
    placed_at: datetime
    snapshot_items: List[OrderItem]
    subtotal_cents: int
    tax_cents: int
    total_cents: int

    class Config:
        orm_mode = True

# JSON example for OrderCreate:
# {
#   "tab_id": 123,
#   "waiter_id": 45,
#   "items": [
#     {"menu_item_id": 10, "name": "Fries", "price_cents": 2500, "qty": 2},
#     {"menu_item_id": 12, "name": "Cola", "price_cents": 1500, "qty": 1}
#   ],
#   "note": "No salt"
# }
```

---

```py
# billo-backend/app/schemas/payment.py
from pydantic import BaseModel, Field, validator
from typing import Literal, Optional, Dict, Any

class PaymentWebhook(BaseModel):
    # Generic webhook payload schema for payment providers.
    # `idempotency_key` must be passed or derived from provider payload to av