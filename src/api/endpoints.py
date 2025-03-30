"""
API endpoints for content generation workflow.

This module defines the FastAPI endpoints for creating, managing,
and monitoring content generation workflows.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Header, BackgroundTasks, Query
from fastapi.responses import JSONResponse

from src.config.settings import settings
from src.models.content_models import ContentRequest, WorkflowStatus, HealthCheckResponse
from src.api.models import (
    ErrorResponse, WorkflowResponse, WorkflowStatusResponse,
    WorkflowListResponse, CancelWorkflowResponse
)
from src.services.workflow_service import workflow_service
from src.services.llm_service import llm_service
from src.utils.validation import validate_api_key

# Set up logger
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix=settings.api.API_PREFIX)


async def verify_api_key(x_api_key: str = Header(None)):
    """Verify API key middleware.
    
    Args:
        x_api_key: API key from request header
        
    Raises:
        HTTPException: If API key is invalid
        
    Returns:
        Validated API key
    """
    if not settings.api.AUTH_REQUIRED:
        return x_api_key
    
    if not x_api_key:
        raise HTTPException(
            status_code=401,
            detail="API key is required",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    if not validate_api_key(x_api_key, settings.api.API_KEYS):
        raise HTTPException(
            status_code=403,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    return x_api_key


@router.get("/health", response_model=HealthCheckResponse, tags=["System"])
async def health_check():
    """Check API health and LLM model availability."""
    model_availability = await llm_service.check_model_availability()
    
    return HealthCheckResponse(
        status="ok",
        version=settings.api.APP_VERSION,
        models=model_availability,
        timestamp=datetime.now()
    )


@router.post(
    "/workflows",
    response_model=WorkflowResponse,
    responses={400: {"model": ErrorResponse}, 401: {"model": ErrorResponse}},
    tags=["Workflows"]
)
async def create_workflow(
    request: ContentRequest,
    api_key: str = Depends(verify_api_key)
):
    """Create a new content generation workflow.
    
    Args:
        request: Content generation request
        api_key: Validated API key
        
    Returns:
        Workflow response with workflow ID
    """
    try:
        workflow_id = await workflow_service.create_workflow(request)
        
        return WorkflowResponse(
            workflow_id=workflow_id,
            message="Workflow created successfully"
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Error creating workflow: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/workflows/{workflow_id}",
    response_model=WorkflowStatusResponse,
    responses={404: {"model": ErrorResponse}, 401: {"model": ErrorResponse}},
    tags=["Workflows"]
)
async def get_workflow_status(
    workflow_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Get workflow status by ID.
    
    Args:
        workflow_id: Workflow ID
        api_key: Validated API key
        
    Returns:
        Workflow status response
    """
    workflow = await workflow_service.get_workflow(workflow_id)
    
    if not workflow:
        raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")
    
    return WorkflowStatusResponse(workflow=workflow)


@router.get(
    "/workflows",
    response_model=WorkflowListResponse,
    responses={401: {"model": ErrorResponse}},
    tags=["Workflows"]
)
async def list_workflows(
    status: Optional[WorkflowStatus] = Query(None, description="Filter by workflow status"),
    limit: int = Query(10, description="Maximum number of workflows to return"),
    offset: int = Query(0, description="Offset for pagination"),
    api_key: str = Depends(verify_api_key)
):
    """List all workflows with optional filtering.
    
    Args:
        status: Filter by workflow status
        limit: Maximum number of workflows to return
        offset: Offset for pagination
        api_key: Validated API key
        
    Returns:
        Workflow list response
    """
    workflows = await workflow_service.list_workflows()
    
    # Apply status filter if provided
    if status:
        workflows = [w for w in workflows if w.status == status]
    
    # Apply pagination
    total_count = len(workflows)
    workflows = workflows[offset:offset + limit]
    
    return WorkflowListResponse(
        workflows=workflows,
        count=total_count
    )


@router.post(
    "/workflows/{workflow_id}/cancel",
    response_model=CancelWorkflowResponse,
    responses={404: {"model": ErrorResponse}, 401: {"model": ErrorResponse}},
    tags=["Workflows"]
)
async def cancel_workflow(
    workflow_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Cancel an active workflow.
    
    Args:
        workflow_id: Workflow ID
        api_key: Validated API key
        
    Returns:
        Cancel workflow response
    """
    workflow = await workflow_service.get_workflow(workflow_id)
    
    if not workflow:
        raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")
    
    cancelled = await workflow_service.cancel_workflow(workflow_id)
    
    return CancelWorkflowResponse(
        workflow_id=workflow_id,
        message="Workflow cancelled successfully" if cancelled else "Workflow was already completed or failed",
        cancelled=cancelled
    )


@router.get(
    "/workflows/{workflow_id}/content",
    responses={404: {"model": ErrorResponse}, 401: {"model": ErrorResponse}},
    tags=["Content"]
)
async def get_generated_content(
    workflow_id: str,
    format: str = Query("html", description="Content format (html, markdown, text)"),
    api_key: str = Depends(verify_api_key)
):
    """Get generated content for a completed workflow.
    
    Args:
        workflow_id: Workflow ID
        format: Content format (html, markdown, text)
        api_key: Validated API key
        
    Returns:
        Generated content in requested format
    """
    workflow = await workflow_service.get_workflow(workflow_id)
    
    if not workflow:
        raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")
    
    if not workflow.generated_content:
        raise HTTPException(status_code=404, detail=f"No content generated for workflow {workflow_id}")
    
    content = workflow.generated_content.full_content
    
    if format == "html":
        # Convert markdown to HTML (simple implementation)
        # In production, use a proper markdown to HTML converter
        html_content = f"<h1>{workflow.generated_content.title}</h1>"
        for section in workflow.generated_content.content_sections:
            html_content += f"<h2>{section.get('heading', '')}</h2>"
            html_content += f"<div>{section.get('content', '').replace('\n', '<br>')}</div>"
        
        return JSONResponse(content={"content": html_content, "format": "html"})
    
    elif format == "text":
        # Convert to plain text
        text_content = f"{workflow.generated_content.title}\n\n"
        for section in workflow.generated_content.content_sections:
            text_content += f"{section.get('heading', '')}\n\n"
            text_content += f"{section.get('content', '')}\n\n"
        
        return JSONResponse(content={"content": text_content, "format": "text"})
    
    else:  # markdown (default)
        return JSONResponse(content={"content": content, "format": "markdown"})
