"""
Brief Agent for content planning.

This agent creates focused content briefs based on research analysis,
identifying content opportunities and structuring recommendations.
"""

import logging
from typing import Dict, Any, Optional

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.storage.base import Storage as StorageProvider

from src.config.settings import settings
from src.config.agno_config import get_knowledge_provider

# Set up logger
logger = logging.getLogger(__name__)


class BriefAgent(Agent):
    """Agent for creating content briefs based on research analysis."""

    def __init__(self, storage: Optional[StorageProvider] = None):
        """Initialize the brief agent.
        
        Args:
            storage: Optional storage provider for persistent state
        """
        super().__init__(
            name="Brief Agent",
            description="Creates content briefs based on research analysis.",
            model=OpenAIChat(id="gpt-4o"),
            storage=storage,
            knowledge=get_knowledge_provider()
        )
    
    async def run(self, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute the brief agent workflow.
        
        Args:
            context: The agent context containing the research results
            
        Returns:
            Content brief
        """
        # Use the context passed or the agent's own context
        context = context or self.context
        
        logger.info("Creating content brief")
        
        # For this simplified version, we'll just call the parent run method
        # with a structured prompt about creating a content brief
        response = await super().run(
            user_message=f"""
            Create a content brief based on the research analysis for the keyword: {context.get('keyword', 'unknown')}.
            
            Include:
            1. Recommended content structure
            2. Key topics to cover
            3. Content differentiation strategy
            4. E-E-A-T signals to include
            
            Format the response as JSON.
            """,
            use_json_mode=True
        )
        
        # Add to context for other agents to use
        if context is not self.context:
            context["content_brief"] = response
        else:
            self.add_context({"content_brief": response})
        
        return response
