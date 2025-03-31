"""
Workflow service for content generation.

This service orchestrates the multi-stage content generation workflow,
managing the execution of individual agents in sequence and maintaining
workflow state.
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, Any, Optional, List

import agno
from agno.team import Team
from agno.workflow import Workflow, RunResponse
from agno.storage.base import Storage as StorageProvider
from agno.storage.json import JsonStorage as MemoryStorage

from src.config.settings import settings
from src.config.agno_config import _get_storage_provider
from src.models.content_models import (
    ContentRequest, WorkflowResult, WorkflowStatus, 
    ResearchOutput, ContentBrief, FactsOutput, GeneratedContent
)
from src.agents.research_agent import ResearchAgent
from src.agents.brief_agent import BriefAgent
from src.agents.facts_agent import FactsAgent
from src.agents.content_agent import ContentAgent
from src.utils.validation import validate_workflow_result

# Set up logger
logger = logging.getLogger(__name__)


class WorkflowService:
    """Service for managing content generation workflows.
    
    This service orchestrates the execution of agents in sequence,
    maintains workflow state, and provides methods for creating,
    retrieving, and updating workflows.
    """
    
    def __init__(self, storage: Optional[StorageProvider] = None):
        """Initialize the workflow service.
        
        Args:
            storage: Optional storage provider for persistence
        """
        # Get the storage provider from our config or use the passed one
        self.storage = storage or _get_storage_provider()
        self.workflows: Dict[str, WorkflowResult] = {}
        self.active_workflows: Dict[str, asyncio.Task] = {}
        
        # Initialize individual agents
        self.research_agent = ResearchAgent(storage=self.storage)
        self.brief_agent = BriefAgent(storage=self.storage)
        self.facts_agent = FactsAgent(storage=self.storage)
        self.content_agent = ContentAgent(storage=self.storage)
        
        # Initialize the agent team with sequential mode (default)
        self.content_team = Team(
            name="Content Creation Team",
            members=[
                self.research_agent,
                self.brief_agent,
                self.facts_agent,
                self.content_agent
            ],
            storage=self.storage
        )
        
        logger.info(f"Workflow service initialized with Agno Team using {settings.agno.TEAM_ORCHESTRATION} orchestration")
    
    async def create_workflow(self, request: ContentRequest) -> str:
        """Create a new content generation workflow.
        
        Args:
            request: Content generation request
            
        Returns:
            Workflow ID
        """
        # Generate workflow ID
        workflow_id = str(uuid.uuid4())
        
        # Create initial workflow state
        workflow = WorkflowResult(
            id=workflow_id,
            status=WorkflowStatus.PENDING,
            request=request,
            created_at=time.time(),
            updated_at=time.time(),
            errors=[]
        )
        
        # Store workflow
        self.workflows[workflow_id] = workflow
        
        # Limit concurrent workflows based on settings
        active_count = len(self.active_workflows)
        if active_count >= settings.agent.CONCURRENT_WORKFLOWS:
            logger.warning(f"Maximum concurrent workflows reached ({active_count}). Queuing workflow {workflow_id}")
            workflow.status = WorkflowStatus.QUEUED
            return workflow_id
        
        # Start workflow execution in background
        self.active_workflows[workflow_id] = asyncio.create_task(
            self._execute_workflow(workflow_id)
        )
        
        logger.info(f"Created workflow {workflow_id} for keyword '{request.keyword}'")
        
        return workflow_id
    
    async def get_workflow(self, workflow_id: str) -> Optional[WorkflowResult]:
        """Get workflow by ID.
        
        Args:
            workflow_id: Workflow ID
            
        Returns:
            Workflow result or None if not found
        """
        return self.workflows.get(workflow_id)
    
    async def list_workflows(self) -> List[WorkflowResult]:
        """List all workflows.
        
        Returns:
            List of all workflow results
        """
        return list(self.workflows.values())
    
    async def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel an active workflow.
        
        Args:
            workflow_id: Workflow ID
            
        Returns:
            True if cancelled, False if not found or already completed
        """
        if workflow_id not in self.workflows:
            return False
        
        workflow = self.workflows[workflow_id]
        
        # Check if workflow is still active
        if workflow.status not in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED]:
            # Cancel background task
            if workflow_id in self.active_workflows:
                self.active_workflows[workflow_id].cancel()
                try:
                    await self.active_workflows[workflow_id]
                except asyncio.CancelledError:
                    pass
                
                del self.active_workflows[workflow_id]
            
            # Update workflow status
            workflow.status = WorkflowStatus.FAILED
            workflow.updated_at = time.time()
            workflow.errors.append({
                "stage": workflow.status,
                "message": "Workflow cancelled by user",
                "timestamp": time.time()
            })
            
            logger.info(f"Cancelled workflow {workflow_id}")
            
            return True
        
        return False
    
    async def _execute_workflow(self, workflow_id: str) -> None:
        """Execute workflow using Agno Team.
        
        Args:
            workflow_id: Workflow ID
        """
        workflow = self.workflows[workflow_id]
        start_time = time.time()
        
        try:
            # Update team context with workflow data instead of using Context
            self.content_team.add_context({
                "workflow_id": workflow_id,
                "keyword": workflow.request.keyword,
                "secondary_keywords": workflow.request.secondary_keywords,
                "content_type": workflow.request.content_type,
                "target_audience": workflow.request.target_audience,
                "tone": workflow.request.tone,
                "brand_voice_guidelines": workflow.request.brand_voice_guidelines,
                "word_count": workflow.request.word_count,
                "extra_instructions": workflow.request.extra_instructions
            })
            
            # Set team session ID to workflow ID for traceability
            self.content_team.session_id = workflow_id
            
            # Execute the team (runs all agents in sequence)
            await self._update_workflow_status(workflow_id, WorkflowStatus.RESEARCH_IN_PROGRESS)
            
            # Run the entire team on the context
            team_result = await self.content_team.run()
            
            # Process results from each agent in the team
            if "research_output" in team_result:
                workflow.research_output = ResearchOutput(**team_result["research_output"])
            
            if "content_brief" in team_result:
                workflow.content_brief = ContentBrief(**team_result["content_brief"])
            
            if "facts_output" in team_result:
                workflow.facts_output = FactsOutput(**team_result["facts_output"])
            
            if "generated_content" in team_result:
                workflow.generated_content = GeneratedContent(**team_result["generated_content"])
            
            # Mark workflow as completed
            workflow.total_execution_time = time.time() - start_time
            await self._update_workflow_status(workflow_id, WorkflowStatus.COMPLETED)
            
            # Validate final result
            validate_workflow_result(workflow)
            
            logger.info(f"Workflow {workflow_id} completed successfully in {workflow.total_execution_time:.2f} seconds")
        
        except asyncio.CancelledError:
            logger.info(f"Workflow {workflow_id} cancelled")
            raise
        
        except Exception as e:
            logger.error(f"Error executing workflow {workflow_id}: {str(e)}")
            
            # Update workflow status
            workflow.status = WorkflowStatus.FAILED
            workflow.updated_at = time.time()
            workflow.total_execution_time = time.time() - start_time
            workflow.errors.append({
                "stage": workflow.status,
                "message": str(e),
                "timestamp": time.time()
            })
            
            # Clean up
            if workflow_id in self.active_workflows:
                del self.active_workflows[workflow_id]
    
    async def _update_workflow_status(self, workflow_id: str, status: WorkflowStatus) -> None:
        """Update workflow status.
        
        Args:
            workflow_id: Workflow ID
            status: New workflow status
        """
        workflow = self.workflows[workflow_id]
        workflow.status = status
        workflow.updated_at = time.time()
        
        logger.info(f"Updated workflow {workflow_id} status to {status}")


# Create global service instance
workflow_service = WorkflowService()
