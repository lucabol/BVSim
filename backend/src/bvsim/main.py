"""Main FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from .core.database import check_database_connection
from .schemas.common import HealthCheck
from .api.rally import router as rally_router
from .api.monte_carlo import router as monte_carlo_router

app = FastAPI(
    title="Beach Volleyball Simulator API",
    description="API for beach volleyball point simulation and statistical analysis",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=dict)
async def root():
    """Root endpoint."""
    return {
        "message": "Beach Volleyball Simulator API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    db_connected = await check_database_connection()
    
    return {
        "status": "healthy" if db_connected else "unhealthy",
        "timestamp": "2025-07-10T15:45:00Z",
        "version": "1.0.0",
        "database_connected": db_connected,
        "uptime_seconds": 0.0,
    }


@app.get("/api/info")
async def api_info():
    """Get API information."""
    return {
        "title": "Beach Volleyball Simulator API",
        "version": "1.0.0",
        "description": "API for beach volleyball point simulation and statistical analysis",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "redoc": "/redoc",
            "teams": "/api/teams",
            "simulations": "/api/simulations",
            "analytics": "/api/analytics"
        },
        "database": {
            "type": "SQLite" if os.getenv("DATABASE_URL", "").startswith("sqlite") else "PostgreSQL",
            "url_set": bool(os.getenv("DATABASE_URL"))
        }
    }


# Include routers
app.include_router(rally_router)
app.include_router(monte_carlo_router)

# Phase 3: Match simulation endpoints
from .api.match import router as match_router
app.include_router(match_router)

# Phase 4: Advanced analytics endpoints
from .api.analytics import router as analytics_router
app.include_router(analytics_router)

# Include additional routers here as they're implemented
# from .routers import teams, simulations
# app.include_router(teams.router, prefix="/api/teams", tags=["teams"])
# app.include_router(simulations.router, prefix="/api/simulations", tags=["simulations"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
