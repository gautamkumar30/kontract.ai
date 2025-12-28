from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from database import engine, Base, get_settings
from logger import setup_logging, get_logger, RequestLoggingMiddleware

# Setup logging
setup_logging(log_level="INFO")
logger = get_logger(__name__)

# Import models to register them with Base before creating tables
import models

# Import routers (will be created)
# from routers import contracts, versions, changes, alerts, webhooks

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Contract Drift Detector API",
    description="API for detecting and tracking changes in SaaS contracts",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Get settings
settings = get_settings()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:5678"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request logging middleware
app.add_middleware(RequestLoggingMiddleware)

logger.info("Application startup - initializing services...")

# Create uploads directory if it doesn't exist
os.makedirs(settings.upload_dir, exist_ok=True)

# Mount uploads directory for serving files
if os.path.exists(settings.upload_dir):
    app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Contract Drift Detector API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "database": "connected"
    }


# Include routers
from routers import contracts, versions, changes, alerts, clauses, stats, analytics

app.include_router(contracts.router, prefix="/api/contracts", tags=["contracts"])
app.include_router(versions.router, prefix="/api/contracts", tags=["versions"])
app.include_router(changes.router, prefix="/api/contracts", tags=["changes"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])
app.include_router(clauses.router, prefix="/api/contracts", tags=["clauses"])
app.include_router(stats.router, prefix="/api", tags=["stats"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
