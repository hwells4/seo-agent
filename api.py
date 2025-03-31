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

from content_creation_team import create_content_team

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

# Create global team instance for reuse
content_team = None

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
    steps: Optional[Dict[str, str]] = None

# Track workflows
workflows = {}

def initialize_team():
    """Initialize the content team if not already done"""
    global content_team
    if content_team is None:
        content_team = create_content_team()
    return content_team

def extract_gap_analysis(brief_content):
    """Extract the gap analysis section from the brief content
    
    Args:
        brief_content (str): The content brief text
        
    Returns:
        str: Extracted gap analysis, or None if not found
    """
    # Try to find a section explicitly labeled as "Gap Analysis"
    pattern = r"(?i)Gap Analysis:?\s*(.*?)(?:\n\n|\n#|\Z)"
    match = re.search(pattern, brief_content, re.DOTALL)
    
    if match:
        return match.group(1).strip()
    
    # If no explicit section, look for content gap mentions
    pattern = r"(?i)content gaps?:?\s*(.*?)(?:\n\n|\n#|\Z)"
    match = re.search(pattern, brief_content, re.DOTALL)
    
    if match:
        return match.group(1).strip()
    
    # Last resort - try to find any paragraph mentioning gaps or opportunities
    pattern = r"(?i)(?:gaps?|opportunities).*?(?:\.\s|$)(.*?)(?:\n\n|\n#|\Z)"
    match = re.search(pattern, brief_content, re.DOTALL)
    
    if match:
        return match.group(0).strip()
    
    # Return a generic message if nothing found
    return "No specific gap analysis found. Focus on gathering current facts and trends."

def run_content_workflow(workflow_id: str, request: ContentRequest):
    """Run the content creation workflow in the background"""
    global workflows
    
    try:
        # Initialize team with brand voice if provided
        team = create_content_team(request.brand_voice.dict() if request.brand_voice else None)
        
        # Prepare prompt
        prompt = f"Create {request.content_type} about {request.topic}. "
        prompt += f"The content should be in a {request.tone} tone and about {request.word_count} words."
        
        # Update status
        workflows[workflow_id]["status"] = "running"
        workflows[workflow_id]["steps"] = {
            "research": "pending",
            "brief": "pending",
            "facts": "pending",
            "content": "pending"
        }
        
        # Run the team
        result = team.run(message=prompt)
        
        # Update workflow with result
        workflows[workflow_id]["status"] = "completed"
        workflows[workflow_id]["result"] = result.content
        workflows[workflow_id]["steps"]["content"] = "completed"
        
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
            "research": "pending",
            "brief": "pending",
            "facts": "pending",
            "content": "pending"
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