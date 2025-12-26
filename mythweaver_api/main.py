"""
Mythweaver API - Main Application Entry Point
AI Narrator RPG Backend
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uvicorn
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine
from app.models import Base
from app.routers import auth, narrator, campaign
from app.middleware.error_handler import setup_error_handlers

# Database initialization
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events"""
    # Startup: Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Test database connection
    try:
        from sqlalchemy import text
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        raise
    
    yield
    
    # Shutdown: Dispose of database engine
    await engine.dispose()
    print("👋 Application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered narrator for interactive RPG storytelling",
    lifespan=lifespan
)

# Setup error handlers for standardized exception handling
setup_error_handlers(app)

# CORS middleware - configured for mobile app development
# In development, allow all localhost origins for Flutter web
if settings.DEBUG:
    allowed_origins = ["*"]  # Allow all origins in development
else:
    allowed_origins = settings.ALLOWED_ORIGINS.split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        from sqlalchemy import text
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        
        # Check if OpenAI API key is configured
        openai_configured = settings.OPENAI_API_KEY is not None
        
        return {
            "status": "healthy",
            "version": settings.APP_VERSION,
            "timestamp": datetime.utcnow().isoformat(),
            "database": "connected",
            "openai_configured": openai_configured
        }
    except Exception as e:
        raise HTTPException(
            status_code=503, 
            detail=f"Service unhealthy: {str(e)}"
        )


# API routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(narrator.router)  # Prefix already defined in router
app.include_router(campaign.router)  # Prefix already defined in router

# Root endpoint
@app.get("/")
async def root():
    """API root - welcome message"""
    return {
        "message": "Welcome to Mythweaver API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )