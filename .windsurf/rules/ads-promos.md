---
trigger: manual
---

Got it 🔥 — here’s the **Appendix: Ads & Promos** section you can tack onto the badass LLM rulebook.

---

# **Appendix: Ads & Promos**

## 1) Purpose

Restaurants can broadcast promotions directly to the **Customer app (BeeWare Android)**. Promotions appear as banners or styled text, optionally clickable for quick ordering.

---

## 2) Promo Types

* **Text Promo:**

  * Text message with selectable background (solid color or image).
  * Font size & emphasis controlled via schema.

* **SVG Banner Promo:**

  * Scalable vector image banner with fixed aspect ratio (recommended 16:9 or 3:1).
  * Must support embedding in customer app screen.

---

## 3) Display Rules

* Display area: customer app home screen → “Promotions” section.
* Promos must be non-intrusive (scrollable list or carousel).
* Customers can tap → navigates to related menu items or special tab (if defined).

---

## 4) Schema (Pydantic)

```py
# billo-backend/app/schemas/promo.py
from pydantic import BaseModel, Field
from typing import Optional, Literal

class PromoCreate(BaseModel):
    restaurant_id: int
    type: Literal["text", "svg"]
    title: str
    body: Optional[str]
    background_color: Optional[str] = None   # e.g. "#FF5733"
    background_image_url: Optional[str] = None
    svg_url: Optional[str] = None
    click_action: Optional[str] = None       # endpoint or menu_item_id reference
    template: Optional[Literal["todays_offer", "time_offer", "two_for_one"]] = None
    starts_at: Optional[str] = None
    ends_at: Optional[str] = None

class PromoOut(PromoCreate):
    id: int
```

---

## 5) Templates (Quick)

* **Today’s Offer** → auto-expiry at midnight.
* **Time-based Offer** → provide start/end timestamps.
* **2-for-1** → template ties promo to menu items (handled by backend logic).

---

## 6) Client Behavior

* **Customer App (BeeWare):**

  * Render text or SVG with background styling.
  * Click → triggers action (open menu item, open tab, pre-fill order).
* **Restaurant PWA:**

  * Admin panel includes “Create Promo” screen with templates.

---

## 7) Business Rules

* Promos are **per restaurant** only.
* Promo lifecycle: `draft → active → expired`.
* Expired promos must disappear automatically.
* Backend ensures only admins can create/update promos.

---

Include a `Promo` SQLAlchemy model + migration (with endpoints `/promos`) so it’s immediately usable in backend + client?
