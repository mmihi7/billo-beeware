---
trigger: manual
---

# Billo MVP - Production System Architecture & Implementation Rules

## Core Business Logic Foundation

### 1. System Architecture Principle
**Rule:** Build a backend-first architecture where all business logic is centralized in the FastAPI server. Clients (Native, PWA, Desktop) are dumb terminals that consume APIs.

### 2. Authentication & Authorization Rules
- **Customers:** Use Supabase Auth (JWT tokens)
- **Waiters:** Custom PIN-based authentication (hashed PINs in database)
- **Admins:** Supabase Auth + admin role validation
- **API Security:** All endpoints must validate JWT tokens or PIN credentials

### 3. Tab Management Logic
**Daily Sequential Number Generation:**
- Tab numbers reset daily per restaurant
- Generate next number: `MAX(tab_number) + 1` for current day/restaurant
- Enforce uniqueness constraint: (restaurant_id, date, tab_number)

**Tab Status Lifecycle:**
- inactive → active → payment_pending → paid ↳ cancelled

### 4. Order Processing Rules
- Orders can only be placed on `active` or `inactive` tabs
- First order on a tab changes status from `inactive` → `active`
- Order total calculated from menu prices at time of ordering (price snapshot)
- Order status flow: `placed → preparing → ready → delivered → completed`

### 5. Payment Processing Logic
**Payment Methods:**
- Cash: Mark as paid by waiter
- Mobile Money: Integrate with payment provider API + webhook confirmation

**Payment States:**
- `pending` → `processing` → `confirmed`/`failed`
- Only confirmed payments close tabs (`paid` status)

### 6. Real-time Communication
- Use Supabase Realtime for live updates
- Implement websocket connections for:
  - Order status updates
  - New messages (customer-waiter chat)
  - Bill updates

## Database Relationship Logic

### Core Entity Relationships
1. **Restaurant** (1) → (N) **Tabs**
2. **Restaurant** (1) → (N) **Menu Items**
3. **Tab** (1) → (N) **Orders**
4. **Tab** (1) → (N) **Payments**
5. **Tab** (1) → (N) **Messages**
6. **Waiter** (1) → (N) **Orders**

### Data Integrity Rules
- Menu item prices snapshot in orders for historical accuracy
- Tab numbers unique per restaurant per day
- Payments reference specific tabs
- All financial amounts stored as integers (cents)

## Function Migration Guide from Kivy Codebase

### ✅ Migrate Directly (Backend/Logic Functions)
These contain pure business logic and can be reused:

1. **Auth Service** (`shared/auth_service.py`):
   - `login`, `logout`, `register` methods
   - `get_current_user` functionality

2. **Database Core** (`shared/database.py`):
   - Connection pooling logic
   - Database initialization

3. **Utility Functions** (`shared/utils.py`):
   - `format_currency`
   - `validate_email`
   - `generate_uuid`

4. **Model Classes** (`shared/models/`):
   - Base model patterns (`save`, `delete`, `to_dict`)
   - Core business models (User, Restaurant, Order, Menu, Item)

5. **API Client Logic** (Various files):
   - Supabase initialization and configuration
   - API call patterns and error handling

### 🔄 Refactor for New Architecture (UI-Related Functions)
These need adaptation for BeeWare/Toga:

1. **Screen Management** (`app.py`):
   - `switch_screen` → Implement with Toga navigation
   - `initialize_screens` → Rewrite for Toga's app structure

2. **QR Scanning** (`qr_scanner_screen.py`):
   - Implement using native platform capabilities via BeeWare
   - `on_qr_detected` logic remains similar

3. **Deep Link Handling** (`app.py`):
   - `handle_deep_link` → Implement with platform-specific intent handling
   - `_on_new_intent` → Adapt for iOS/Android deep linking

### ❌ Rewrite Completely (Kivy-Specific Code)
These are tightly coupled to Kivy and must be reimplemented:

1. **Kivy UI Components** (All `.kv` files and UI code):
   - Complete rewrite using Toga widgets
   - Layout management and styling

2. **Kivy-Specific Lifecycle** (`app.py`):
   - `build` method
   - `_init_platform` (replace with BeeWare platform config)
   - Kivy-specific event handlers

3. **Kivy Async Integration** (`_init_async`):
   - Replace with native async/await patterns in FastAPI/BeeWare

## Implementation Priority Order

1. **Phase 1:** FastAPI Backend + Database Schema
2. **Phase 2:** React PWA (reference client)
3. **Phase 3:** BeeWare Native Mobile App
4. **Phase 4:** BeeWare Desktop App
5. **Phase 5:** Demo System (static mock data)

## Critical Security Rules

1. Never store plain text PINs - always hash with salt
2. Validate all API inputs rigorously
3. Implement rate limiting on auth endpoints
4. Use HTTPS exclusively in production
5. Regular security audits of third-party dependencies

## Monitoring & Analytics Requirements

1. Track tab creation and completion rates
2. Monitor order preparation times
3. Record payment success/failure rates
4. Log customer-waiter message volumes
5. Track feature adoption across client types