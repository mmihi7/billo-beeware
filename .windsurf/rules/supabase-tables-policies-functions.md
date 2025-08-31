---
trigger: manual
description: supabase-tables-policies-functions
---

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =========================================================
-- 1. Restaurants
-- =========================================================
DROP TABLE IF EXISTS restaurants CASCADE;

CREATE TABLE restaurants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    address TEXT,
    phone TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_by UUID, -- will later reference profiles
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =========================================================
-- 2. Profiles
-- =========================================================
DROP TABLE IF EXISTS profiles CASCADE;

CREATE TABLE profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE,
    full_name TEXT,
    pin TEXT, -- for waiters only
    role TEXT NOT NULL CHECK (role IN ('admin','waiter','customer')),
    restaurant_id UUID REFERENCES restaurants(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- backfill foreign key for created_by in restaurants
ALTER TABLE restaurants
    ADD CONSTRAINT fk_restaurants_created_by
    FOREIGN KEY (created_by) REFERENCES profiles(id);

-- =========================================================
-- 3. Business Hours
-- =========================================================
DROP TABLE IF EXISTS business_hours CASCADE;

CREATE TABLE business_hours (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    restaurant_id UUID NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    day_of_week SMALLINT NOT NULL CHECK (day_of_week BETWEEN 0 AND 6),
    open_time TIME,
    close_time TIME,
    is_closed BOOLEAN NOT NULL DEFAULT FALSE
);

-- =========================================================
-- 4. Tabs
-- =========================================================
DROP TABLE IF EXISTS tabs CASCADE;

CREATE TABLE tabs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    restaurant_id UUID NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    tab_number INTEGER NOT NULL,
    status TEXT NOT NULL CHECK (
        status IN ('inactive','active','payment_pending','paid','cancelled')
    ),
    opened_by UUID REFERENCES profiles(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    tab_date DATE NOT NULL DEFAULT CURRENT_DATE,
    CONSTRAINT unique_tab_per_user_per_day UNIQUE (restaurant_id, opened_by, tab_date)
);

-- =========================================================
-- 5. Menu Items
-- =========================================================
DROP TABLE IF EXISTS menu_items CASCADE;

CREATE TABLE menu_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    restaurant_id UUID NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    category TEXT,
    is_available BOOLEAN NOT NULL DEFAULT TRUE,
    is_featured BOOLEAN NOT NULL DEFAULT FALSE,
    image_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =========================================================
-- 6. Orders
-- =========================================================
DROP TABLE IF EXISTS orders CASCADE;

CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tab_id UUID NOT NULL REFERENCES tabs(id) ON DELETE CASCADE,
    waiter_id UUID REFERENCES profiles(id),
    status TEXT NOT NULL CHECK (
        status IN ('pending','accepted','preparing','completed')
    ),
    total_amount DECIMAL(10,2) NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =========================================================
-- 7. Order Items
-- =========================================================
DROP TABLE IF EXISTS order_items CASCADE;

CREATE TABLE order_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    menu_item_id UUID NOT NULL REFERENCES menu_items(id),
    quantity INTEGER NOT NULL DEFAULT 1,
    special_requests TEXT,
    status TEXT NOT NULL CHECK (
        status IN ('pending','preparing','ready','served')
    ),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =========================================================
-- 8. Promos
-- =========================================================
DROP TABLE IF EXISTS promos CASCADE;

CREATE TABLE promos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    restaurant_id UUID NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    discount_type TEXT NOT NULL CHECK (discount_type IN ('percentage','fixed','bogo')),
    discount_value DECIMAL(10,2) NOT NULL,
    start_date TIMESTAMPTZ NOT NULL,
    end_date TIMESTAMPTZ NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =========================================================
-- 9. Chats
-- =========================================================
DROP TABLE IF EXISTS chats CASCADE;

CREATE TABLE chats (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    restaurant_id UUID NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    tab_id UUID NOT NULL REFERENCES tabs(id) ON DELETE CASCADE,
    sender_id UUID NOT NULL REFERENCES profiles(id),
    message TEXT NOT NULL,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE tabs ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE order_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE promos ENABLE ROW LEVEL SECURITY;
ALTER TABLE chats ENABLE ROW LEVEL SECURITY;
ALTER TABLE menu_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE restaurants ENABLE ROW LEVEL SECURITY;

-- Allow user to select their own profile
CREATE POLICY select_own_profile ON profiles
FOR SELECT USING (auth.uid() = id);

-- Allow user to update their own profile
CREATE POLICY update_own_profile ON profiles
FOR UPDATE USING (auth.uid() = id);

-- Allow admins to view and manage waiters in their restaurant
CREATE POLICY admin_manage_waiters ON profiles
FOR ALL
USING (
  role = 'waiter'
  AND restaurant_id IN (
    SELECT restaurant_id FROM profiles WHERE id = auth.uid() AND role = 'admin'
  )
);

-- Admin can view/edit their restaurant
CREATE POLICY admin_restaurant_access ON restaurants
FOR ALL
USING (id IN (
  SELECT restaurant_id FROM profiles WHERE id = auth.uid() AND role = 'admin'
));

-- Customer can see their own tabs
CREATE POLICY customer_tabs ON tabs
FOR SELECT USING (opened_by = auth.uid());

-- Customer can insert tab (system ensures uniqueness with trigger)
CREATE POLICY customer_create_tab ON tabs
FOR INSERT WITH CHECK (opened_by = auth.uid());

-- Waiters can view tabs in their restaurant
CREATE POLICY waiter_view_tabs ON tabs
FOR SELECT USING (
  restaurant_id IN (
    SELECT restaurant_id FROM profiles WHERE id = auth.uid() AND role = 'waiter'
  )
);

-- Customer can view orders in their own tabs
CREATE POLICY customer_view_orders ON orders
FOR SELECT USING (
  tab_id IN (SELECT id FROM tabs WHERE opened_by = auth.uid())
);

-- Waiter can view/manage orders for their restaurant
CREATE POLICY waiter_manage_orders ON orders
FOR ALL USING (
  tab_id IN (
    SELECT t.id FROM tabs t
    JOIN profiles p ON t.restaurant_id = p.restaurant_id
    WHERE p.id = auth.uid() AND p.role = 'waiter'
  )
);
-- Sender can read their own messages
CREATE POLICY sender_view_chats ON chats
FOR SELECT USING (sender_id = auth.uid());

-- Customers see chats in their own tabs
CREATE POLICY customer_chat_access ON chats
FOR SELECT USING (
  tab_id IN (SELECT id FROM tabs WHERE opened_by = auth.uid())
);

-- Waiters see chats for their restaurant
CREATE POLICY waiter_chat_access ON chats
FOR SELECT USING (
  restaurant_id IN (
    SELECT restaurant_id FROM profiles WHERE id = auth.uid() AND role = 'waiter'
  )
);

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to tables
CREATE TRIGGER update_tabs_updated_at
BEFORE UPDATE ON tabs
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER update_orders_updated_at
BEFORE UPDATE ON orders
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE OR REPLACE FUNCTION enforce_one_tab_per_day()
RETURNS TRIGGER AS $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM tabs
    WHERE opened_by = NEW.opened_by
      AND restaurant_id = NEW.restaurant_id
      AND tab_date = CURRENT_DATE
      AND status IN ('active','inactive','payment_pending')
  ) THEN
    RAISE EXCEPTION 'User already has an open tab today';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER one_tab_per_day
BEFORE INSERT ON tabs
FOR EACH ROW EXECUTE FUNCTION enforce_one_tab_per_day();




