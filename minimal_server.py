import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Create API app
app = FastAPI(
    title="SEO Agent API", 
    description="API for generating SEO-optimized content",
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

@app.on_event("startup")
async def startup_event():
    """Log when the server starts"""
    logger.info("Server starting up...")
    logger.info("CORS configured with allow_origins=*")

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint for monitoring"""
    logger.info("Health check endpoint called")
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting server...")
    uvicorn.run(app, host="0.0.0.0", port=8000) 