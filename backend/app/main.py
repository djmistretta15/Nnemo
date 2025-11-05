"""
Main FastAPI application for Mnemo platform
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db

# Import routers
from app.api import auth, nodes, marketplace, contracts, websocket, payments, analytics, clusters

# Create FastAPI app
app = FastAPI(
    title="MNEMO - Memory Arbitrage Platform",
    description="VRAM/RAM-as-a-Service marketplace for AI teams",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(nodes.router)
app.include_router(marketplace.router)
app.include_router(contracts.router)
app.include_router(payments.router)
app.include_router(analytics.router)
app.include_router(clusters.router)
app.include_router(websocket.router)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()
    print("✓ Database initialized")
    print(f"✓ MNEMO API running on {settings.API_HOST}:{settings.API_PORT}")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "MNEMO API",
        "version": "1.0.0",
        "description": "Memory Arbitrage Platform",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD
    )
