"""
FastAPI Application
Main entry point for the Agentic Travel Planner API.

Why FastAPI?
============
1. **Async Support**: Native async/await - perfect for LangGraph's async workflow
2. **Auto Documentation**: Swagger UI and ReDoc generated automatically
3. **Type Safety**: Pydantic integration for request/response validation
4. **Performance**: One of the fastest Python frameworks (Starlette + Uvicorn)
5. **Modern Python**: Built for Python 3.7+ with type hints
6. **Easy Testing**: Built-in test client for unit/integration tests
7. **Production Ready**: Used by Microsoft, Netflix, Uber, etc.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
from datetime import datetime

from src.api.routes import travel_router
from src.api.dependencies import get_settings


# ============================================
# LIFESPAN - Startup and Shutdown Events
# ============================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle.
    Code before yield runs on startup.
    Code after yield runs on shutdown.
    """
    # Startup
    print("\n" + "=" * 60)
    print("🚀 AGENTIC TRAVEL PLANNER API")
    print("=" * 60)
    print(f"Starting up at {datetime.now().isoformat()}")
    
    # Verify LangGraph is available
    try:
        from src.agents.travel_graph import travel_planning_app
        print("✓ LangGraph workflow loaded")
    except Exception as e:
        print(f"⚠ LangGraph warning: {e}")
    
    # Verify LLM configuration
    try:
        from src.api.dependencies import verify_api_key
        verify_api_key()
        print("✓ LLM API key configured")
    except Exception as e:
        print(f"⚠ LLM warning: {e}")
    
    settings = get_settings()
    print(f"✓ Running in {'DEBUG' if settings.debug else 'PRODUCTION'} mode")
    print("=" * 60 + "\n")
    
    yield  # Application runs here
    
    # Shutdown
    print("\n" + "=" * 60)
    print("👋 Shutting down API...")
    print("=" * 60 + "\n")


# ============================================
# CREATE FASTAPI APPLICATION
# ============================================

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="""
## 🌍 Agentic Travel Planner API

An AI-powered travel planning API that uses **LangGraph** to orchestrate 
multiple specialized agents for comprehensive trip planning.

### Features

- 🛫 **Flight Search**: Find and compare flights with AI recommendations
- 🏨 **Hotel Search**: Discover accommodations matching your preferences
- 🎯 **Activity Planning**: Get personalized activity suggestions
- 💰 **Budget Optimization**: Automatic budget analysis and optimization
- 📋 **Trip Summary**: AI-generated engaging trip summaries

### How It Works

1. Submit your trip requirements via `/api/v1/plan-trip`
2. Our AI agents search for flights, hotels, and activities
3. Budget is analyzed and optimized if needed
4. Receive a complete trip plan with recommendations

### Architecture

```
┌─────────────────────────────────────────────┐
│              FastAPI Backend                │
├─────────────────────────────────────────────┤
│                 LangGraph                   │
│  ┌─────────┐ ┌─────────┐ ┌──────────────┐  │
│  │ Flight  │→│ Hotel   │→│  Activity    │  │
│  │ Search  │ │ Search  │ │   Search     │  │
│  └─────────┘ └─────────┘ └──────────────┘  │
│       ↓           ↓            ↓           │
│  ┌─────────────────────────────────────┐   │
│  │         Budget Analysis             │   │
│  └─────────────────────────────────────┘   │
│                    ↓                       │
│  ┌─────────────────────────────────────┐   │
│  │         Generate Summary            │   │
│  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```
    """,
    version=settings.app_version,
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc
    openapi_url="/openapi.json",
    lifespan=lifespan
)


# ============================================
# MIDDLEWARE
# ============================================

# CORS - Allow cross-origin requests (required for frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_timing_header(request: Request, call_next):
    """Add response timing header for performance monitoring."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.3f}s"
    return response


# ============================================
# EXCEPTION HANDLERS
# ============================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle any unhandled exceptions gracefully."""
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "message": "An unexpected error occurred",
                "code": "INTERNAL_ERROR",
                "details": str(exc) if settings.debug else None
            }
        }
    )


# ============================================
# INCLUDE ROUTERS
# ============================================

app.include_router(travel_router)


# ============================================
# ROOT ENDPOINTS
# ============================================

@app.get("/", tags=["Root"])
async def root():
    """
    API Root - Welcome message and links to documentation.
    """
    return {
        "message": "Welcome to the Agentic Travel Planner API! 🌍",
        "version": settings.app_version,
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        },
        "endpoints": {
            "plan_trip": "/api/v1/plan-trip",
            "health": "/api/v1/health",
            "destinations": "/api/v1/destinations/popular",
            "interests": "/api/v1/interests"
        }
    }


# ============================================
# MAIN - Run with Uvicorn
# ============================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )
