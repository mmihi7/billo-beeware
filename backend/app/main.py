from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.endpoints import auth, tabs, orders, payments, restaurants

app = FastAPI(
    title="Billo API",
    version=settings.APP_VERSION,
    description="Backend API for Billo Restaurant Tab System"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(tabs.router, prefix="/tabs", tags=["tabs"])
app.include_router(orders.router, prefix="/orders", tags=["orders"])
app.include_router(payments.router, prefix="/payments", tags=["payments"])
app.include_router(restaurants.router, prefix="/restaurants", tags=["restaurants"])

@app.get("/")
async def root():
    return {"message": "Billo API", "version": settings.APP_VERSION}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}