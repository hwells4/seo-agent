"""
API request and response models.

This module defines the data models for API requests and responses,
providing request validation and response formatting.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from src.models.content_models import (
    ContentRequest, WorkflowResult, WorkflowStatus,
    HealthCheckResponse
)


class ErrorResponse(BaseModel):
    """API error response model."""
    status: str = "error"
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")


class WorkflowResponse(BaseModel):
    """API response for workflow operations."""
    status: str = "success"
    workflow_id: str = Field(..., description="Workflow ID")
    message: str = Field(..., description="Response message")


class WorkflowStatusResponse(BaseModel):
    """API response for workflow status."""
    status: str = "success"
    workflow: WorkflowResult = Field(..., description="Workflow details")


class WorkflowListResponse(BaseModel):
    """API response for listing workflows."""
    status: str = "success"
    workflows: List[WorkflowResult] = Field(..., description="List of workflows")
    count: int = Field(..., description="Total number of workflows")


class CancelWorkflowResponse(BaseModel):
    """API response for cancelling a workflow."""
    status: str = "success"
    workflow_id: str = Field(..., description="Workflow ID")
    message: str = Field(..., description="Response message")
    cancelled: bool = Field(..., description="Whether the workflow was cancelled")
