#!/usr/bin/env python3
"""
API for the Content Creation Team
A simple FastAPI implementation that exposes the content creation workflow
"""

import os
import re
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Import from the new structure but keep the same functionality
from agents.content import run_content_pipeline, extract_gap_analysis

# Load environment variables
load_dotenv()

# Create API app
app = FastAPI(title="Content Creation API", description="API for generating content with specialized agents")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class BrandVoice(BaseModel):
    """Model for brand voice configuration"""
    tone: str = Field(default="Professional and authoritative", description="The overall tone of the content")
    style: str = Field(default="Clear, concise, and engaging", description="Writing style to be used")
    sentence_structure: str = Field(default="Varied sentence length with a mix of simple and complex structures", description="Guidelines for sentence construction")
    language: str = Field(default="Use industry terminology appropriately, but explain complex concepts clearly", description="Language usage guidance")
    taboo_words: List[str] = Field(default=["clearly", "obviously", "simply", "just"], description="Words to avoid in content")
    persuasion: str = Field(default="Use evidence-based arguments, social proof, and specific examples", description="Persuasion techniques to employ")
    format: str = Field(default="Use clear headings, bullet points for lists, and short paragraphs", description="Content formatting guidance")

class ContentRequest(BaseModel):
    """Request model for content creation"""
    topic: str = Field(..., description="The main topic for content creation")
    content_type: str = Field(default="blog post", description="Type of content to create (e.g. blog post, article, guide)")
    tone: str = Field(default="helpful", description="Overall tone of the content")
    word_count: int = Field(default=500, description="Target word count for the content", ge=100, le=2000)
    brand_voice: Optional[BrandVoice] = Field(default=None, description="Brand voice configuration")

class ContentResponse(BaseModel):
    """Response model for content creation"""
    workflow_id: str
    status: str
    message: str

class WorkflowStatusResponse(BaseModel):
    """Response model for workflow status"""
    workflow_id: str
    status: str
    request: Optional[Dict[str, Any]] = None
    result: Optional[str] = None
    error: Optional[str] = None
    steps: Optional[Dict[str, Dict[str, Any]]] = None

# Track workflows
workflows = {}

def run_content_workflow(workflow_id: str, request: ContentRequest):
    """Run the content creation pipeline in the background"""
    global workflows
    
    try:
        # Update status
        workflows[workflow_id]["status"] = "running"
        workflows[workflow_id]["steps"] = {
            "research": {"status": "pending"},
            "brief": {"status": "pending"},
            "facts": {"status": "pending"},
            "content": {"status": "pending"}
        }
        
        # Convert brand voice to dict if provided
        brand_voice_dict = request.brand_voice.dict() if request.brand_voice else None
        
        # Run the pipeline with individual agents
        results = run_content_pipeline(
            topic=request.topic,
            brand_voice=brand_voice_dict,
            word_count=request.word_count,
            save_results=True
        )
        
        # Update workflow with results
        workflows[workflow_id]["status"] = "completed"
        workflows[workflow_id]["result"] = results["steps"]["content"]["output"]
        
        # Update step statuses
        workflows[workflow_id]["steps"]["research"] = {
            "status": "completed",
            "output": results["steps"]["research"]["output"]
        }
        
        workflows[workflow_id]["steps"]["brief"] = {
            "status": "completed",
            "output": results["steps"]["brief"]["output"],
            "gap_analysis": results["steps"]["brief"]["extracted_gap_analysis"]
        }
        
        workflows[workflow_id]["steps"]["facts"] = {
            "status": "completed",
            "output": results["steps"]["facts"]["output"]
        }
        
        workflows[workflow_id]["steps"]["content"] = {
            "status": "completed",
            "output": results["steps"]["content"]["output"]
        }
        
    except Exception as e:
        # Handle errors
        workflows[workflow_id]["status"] = "failed"
        workflows[workflow_id]["error"] = str(e)

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    # Set API keys from environment
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")
    os.environ["ANTHROPIC_API_KEY"] = os.getenv("ANTHROPIC_API_KEY", "")
    os.environ["DEEPSEEK_API_KEY"] = os.getenv("DEEPSEEK_API_KEY", "")
    os.environ["XAI_API_KEY"] = os.getenv("XAI_API_KEY", "")

@app.post("/api/v1/content", response_model=ContentResponse)
async def create_content(request: ContentRequest, background_tasks: BackgroundTasks):
    """Create new content based on the request"""
    import uuid
    
    # Generate workflow ID
    workflow_id = str(uuid.uuid4())
    
    # Initialize workflow tracking
    workflows[workflow_id] = {
        "status": "pending",
        "request": request.dict(),
        "steps": {
            "research": {"status": "pending"},
            "brief": {"status": "pending"},
            "facts": {"status": "pending"},
            "content": {"status": "pending"}
        }
    }
    
    # Start background task
    background_tasks.add_task(run_content_workflow, workflow_id, request)
    
    return ContentResponse(
        workflow_id=workflow_id,
        status="pending",
        message="Content creation started"
    )

@app.get("/api/v1/workflows/{workflow_id}", response_model=WorkflowStatusResponse)
async def get_workflow_status(workflow_id: str):
    """Get the status of a workflow"""
    if workflow_id not in workflows:
        return WorkflowStatusResponse(
            workflow_id=workflow_id,
            status="not_found"
        )
    
    workflow = workflows[workflow_id]
    
    return WorkflowStatusResponse(
        workflow_id=workflow_id,
        status=workflow["status"],
        request=workflow["request"] if "request" in workflow else None,
        result=workflow.get("result"),
        error=workflow.get("error"),
        steps=workflow.get("steps")
    )

# Run the API with uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True) 