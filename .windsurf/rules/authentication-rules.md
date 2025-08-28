---
trigger: model_decision
description: When working on authentication issues
---

Restaurant PWA (Python web):
Session-based cookies for browser-based access
Ideal for admin and waiter interfaces
Already implemented in the current codebase
Customer Android App (BeeWare):
JWT token-based authentication
Better suited for mobile apps
Will be implemented in the mobile app
Backend (FastAPI):
Supports both session and JWT authentication
Session middleware for PWA
JWT Bearer auth for mobile
This hybrid approach provides the best of both worlds:

Seamless session management for web users
Stateless JWT for mobile clients
Secure and scalable authentication