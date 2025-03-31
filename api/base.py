#!/usr/bin/env python3
"""
API for the SEO Agent System - A FastAPI implementation that provides access to 
various agent pipelines through a unified RESTful interface.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

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

# Set API keys on startup
@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    # Set API keys from environment
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")
    os.environ["ANTHROPIC_API_KEY"] = os.getenv("ANTHROPIC_API_KEY", "")
    os.environ["DEEPSEEK_API_KEY"] = os.getenv("DEEPSEEK_API_KEY", "")
    os.environ["XAI_API_KEY"] = os.getenv("XAI_API_KEY", "")

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
def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "ok"
    }

# Run the API with uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.base:app", host="0.0.0.0", port=8000, reload=True) 