"""
Main FastAPI Application
Entry point for the Property Management API
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import time

from app.config import settings
from app.database import close_db, init_db

# Import routers (we'll create these)
# from app.api import auth, properties, units, tenants, invoices, payments, mpesa

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager for the application.
    Code before yield runs on startup.
    Code after yield runs on shutdown.
    """
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Database: {settings.DATABASE_URL.split('@')[1]}")  # Hide credentials
    
    # Initialize database (create tables if they don't exist)
    # NOTE: In production, use Alembic migrations instead
    if settings.ENVIRONMENT == "development":
        logger.info("Initializing database tables...")
        init_db()
    
    # TODO: Start scheduled jobs (cron)
    # TODO: Initialize M-Pesa registration
    
    logger.info("Application startup complete!")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    close_db()
    logger.info("Application shutdown complete!")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Property Management System with M-Pesa Integration",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


# =============================================================================
# MIDDLEWARE
# =============================================================================

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Log all HTTP requests with timing information
    """
    start_time = time.time()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url.path}")
    
    # Process request
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    
    # Log response
    logger.info(
        f"Response: {request.method} {request.url.path} "
        f"- Status: {response.status_code} - Time: {process_time:.3f}s"
    )
    
    # Add custom header with processing time
    response.headers["X-Process-Time"] = str(process_time)
    
    return response


# =============================================================================
# EXCEPTION HANDLERS
# =============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled errors
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc) if settings.DEBUG else "An error occurred"
        }
    )


# =============================================================================
# ROUTES
# =============================================================================

@app.get("/")
async def root():
    """
    Root endpoint - API information
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint
    Used by load balancers and monitoring tools
    """
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "version": settings.APP_VERSION
    }


@app.get("/info")
async def app_info():
    """
    Application information endpoint
    """
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "database": "connected",
        "mpesa_environment": settings.MPESA_ENVIRONMENT,
        "sms_enabled": settings.SMS_ENABLED,
        "email_enabled": settings.EMAIL_ENABLED,
    }


# =============================================================================
# API ROUTERS
# =============================================================================

# Import routers
from app.api import auth, properties, units, tenants, invoices, payments, mpesa, cron, reports, bulk, exports

# Include API routers with prefix /api
app.include_router(auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["Authentication"])
app.include_router(properties.router, prefix=settings.API_V1_PREFIX, tags=["Properties"])
app.include_router(units.router, prefix=settings.API_V1_PREFIX, tags=["Units"])
app.include_router(tenants.router, prefix=settings.API_V1_PREFIX, tags=["Tenants"])
app.include_router(invoices.router, prefix=settings.API_V1_PREFIX, tags=["Invoices"])
app.include_router(payments.router, prefix=settings.API_V1_PREFIX, tags=["Payments"])
app.include_router(mpesa.router, prefix=settings.API_V1_PREFIX, tags=["M-Pesa"])
app.include_router(cron.router, prefix=settings.API_V1_PREFIX, tags=["Cron Jobs"])
app.include_router(reports.router, prefix=settings.API_V1_PREFIX, tags=["Reports"])
app.include_router(bulk.router, prefix=settings.API_V1_PREFIX, tags=["Bulk Operations"])
app.include_router(exports.router, prefix=settings.API_V1_PREFIX, tags=["Exports"])


# =============================================================================
# STARTUP MESSAGE
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting {settings.APP_NAME}...")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,  # Auto-reload on code changes in development
        log_level=settings.LOG_LEVEL.lower(),
    )