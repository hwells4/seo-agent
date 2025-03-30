"""
Main application module.

This module initializes and configures the FastAPI application,
including routes, middleware, and error handling.
"""

import logging
from typing import Dict, Any

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from src.config.settings import settings
from src.config.agno_config import init_agno
from src.api.endpoints import router as api_router
from src.api.models import ErrorResponse

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.api.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

# Initialize Agno framework
init_agno()

# Create FastAPI application
app = FastAPI(
    title=settings.api.APP_NAME,
    description=settings.api.APP_DESCRIPTION,
    version=settings.api.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.api.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Add global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler for unhandled exceptions.
    
    Args:
        request: FastAPI request
        exc: Exception that was raised
        
    Returns:
        JSON response with error details
    """
    logger.exception(f"Unhandled exception: {str(exc)}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            message="Internal server error",
            details={"error": str(exc)} if settings.api.DEBUG else None
        ).dict(),
    )


# Include API routes
app.include_router(api_router)


# Root route
@app.get("/", tags=["System"])
async def root() -> Dict[str, Any]:
    """Root endpoint for the API.
    
    Returns:
        Basic API information
    """
    return {
        "name": settings.api.APP_NAME,
        "version": settings.api.APP_VERSION,
        "docs": "/docs",
    }


# Run application when executed directly
if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=settings.api.HOST,
        port=settings.api.PORT,
        reload=settings.api.DEBUG,
    )
