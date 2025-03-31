from fastapi import FastAPI

app = FastAPI()

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "ok"} 