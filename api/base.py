#!/usr/bin/env python3
"""
API for the SEO Agent System - A FastAPI implementation that provides access to 
various agent pipelines through a unified RESTful interface.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import logging
import datetime

from api.routers import content

# Load environment variables
load_dotenv()

# Create API app
app = FastAPI(
    title="SEO Agent API", 
    description="API for generating SEO-optimized content and other services with specialized AI agents",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(content.router)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Set API keys on startup
@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("Starting SEO Agent API...")
    
    # Log environment status (without exposing values)
    api_keys = {
        "OPENAI_API_KEY": bool(os.getenv("OPENAI_API_KEY")),
        "ANTHROPIC_API_KEY": bool(os.getenv("ANTHROPIC_API_KEY")),
        "DEEPSEEK_API_KEY": bool(os.getenv("DEEPSEEK_API_KEY")),
        "XAI_API_KEY": bool(os.getenv("XAI_API_KEY"))
    }
    logger.info(f"API Keys configured: {api_keys}")

# Root endpoint
@app.get("/")
def read_root():
    """Root endpoint that provides basic API information"""
    return {
        "status": "online",
        "message": "Welcome to the SEO Agent API",
        "endpoints": [
            "/api/v1/content",
            "/api/v1/content/workflows/{workflow_id}"
        ]
    }

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint for monitoring"""
    try:
        return {
            "status": "ok",
            "timestamp": datetime.datetime.now().isoformat(),
            "api_version": "1.0.0",
            "environment": {
                "OPENAI_API_KEY": "configured" if os.getenv("OPENAI_API_KEY") else "missing",
                "ANTHROPIC_API_KEY": "configured" if os.getenv("ANTHROPIC_API_KEY") else "missing",
                "DEEPSEEK_API_KEY": "configured" if os.getenv("DEEPSEEK_API_KEY") else "missing",
                "XAI_API_KEY": "configured" if os.getenv("XAI_API_KEY") else "missing"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.datetime.now().isoformat()
        }

# Run the API with uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.base:app", host="0.0.0.0", port=8000, reload=True) 