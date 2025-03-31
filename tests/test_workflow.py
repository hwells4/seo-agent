"""
Simple test harness for the workflow API.

This test allows you to test the workflow API endpoints in development
without needing to mock all the LLM calls. It uses a FastAPI TestClient
to make real API requests and demonstrates how to structure workflow tests.
"""

import os
import pytest
from fastapi.testclient import TestClient
import json
from datetime import datetime

from src.main import app
from src.config.settings import settings
from src.models.content_models import ContentRequest, WorkflowStatus


# Create test client
client = TestClient(app)


def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "models" in data
    assert "timestamp" in data


def test_create_workflow():
    """Test creating a workflow.
    
    This test demonstrates how to create a workflow using the API.
    It doesn't need mocking since the workflow can be created even
    if the agent execution would fail later.
    """
    # Test data
    test_data = {
        "keyword": "test keyword",
        "content_type": "blog post",
        "tone": "professional"
    }
    
    # Make API call with a valid API key from settings
    api_key = settings.api.API_KEYS[0] if settings.api.API_KEYS else "your-api-key-1"
    response = client.post(
        "/api/v1/workflows",
        headers={"X-API-Key": api_key},
        json=test_data
    )
    
    # Validate response
    assert response.status_code == 200
    data = response.json()
    assert "workflow_id" in data
    assert data["message"] == "Workflow created successfully"
    
    # Return workflow ID for further tests
    return data["workflow_id"]


def test_workflow_status():
    """Test retrieving workflow status.
    
    This test demonstrates how to retrieve the status of a workflow.
    """
    # Create a workflow first
    workflow_id = test_create_workflow()
    assert workflow_id is not None
    
    # Get API key
    api_key = settings.api.API_KEYS[0] if settings.api.API_KEYS else "your-api-key-1"
    
    # Make API call to check status
    response = client.get(
        f"/api/v1/workflows/{workflow_id}",
        headers={"X-API-Key": api_key}
    )
    
    # Validate response
    assert response.status_code == 200
    data = response.json()
    assert "workflow" in data
    assert data["workflow"]["id"] == workflow_id
    
    # Workflow will likely fail due to missing API keys or other issues in test,
    # but this confirms the API itself works correctly
    assert "status" in data["workflow"]


def test_workflow_cancellation():
    """Test cancelling a workflow."""
    # Create a workflow first
    workflow_id = test_create_workflow()
    assert workflow_id is not None
    
    # Get API key
    api_key = settings.api.API_KEYS[0] if settings.api.API_KEYS else "your-api-key-1"
    
    # Make API call to cancel workflow
    response = client.post(
        f"/api/v1/workflows/{workflow_id}/cancel",
        headers={"X-API-Key": api_key}
    )
    
    # Validate response
    assert response.status_code == 200
    data = response.json()
    assert data["workflow_id"] == workflow_id


def test_list_workflows():
    """Test listing all workflows."""
    # Create a workflow first to ensure there's something to list
    test_create_workflow()
    
    # Get API key
    api_key = settings.api.API_KEYS[0] if settings.api.API_KEYS else "your-api-key-1"
    
    # Make API call to list workflows
    response = client.get(
        "/api/v1/workflows",
        headers={"X-API-Key": api_key}
    )
    
    # Validate response
    assert response.status_code == 200
    data = response.json()
    assert "workflows" in data
    assert "count" in data
    assert isinstance(data["workflows"], list)
    assert data["count"] >= 1  # At least one workflow should exist


# For manual testing
if __name__ == "__main__":
    print("Running manual API tests...")
    
    # Test health check
    print("\n1. Testing health check...")
    test_health_check()
    print("✅ Health check passed")
    
    # Test workflow creation
    print("\n2. Testing workflow creation...")
    workflow_id = test_create_workflow()
    print(f"✅ Workflow created with ID: {workflow_id}")
    
    # Test workflow status
    print("\n3. Testing workflow status...")
    test_workflow_status()
    print("✅ Workflow status check passed")
    
    # Test workflow list
    print("\n4. Testing workflow listing...")
    test_list_workflows()
    print("✅ Workflow listing passed")
    
    # Test workflow cancellation
    print("\n5. Testing workflow cancellation...")
    test_workflow_cancellation()
    print("✅ Workflow cancellation passed")
    
    print("\nAll tests completed successfully!") 