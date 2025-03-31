"""
Facts Agent for gathering factual information.

This agent gathers up-to-date factual information to enhance content
quality and relevance based on the content brief.
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


class FactsAgent(Agent):
    """Agent for gathering factual information based on content brief."""

    def __init__(self, storage: Optional[StorageProvider] = None):
        """Initialize the facts agent.
        
        Args:
            storage: Optional storage provider for persistent state
        """
        super().__init__(
            name="Facts Agent",
            description="Gathers factual information for content enhancement.",
            model=OpenAIChat(id="gpt-4o"),
            storage=storage,
            knowledge=get_knowledge_provider()
        )
    
    async def run(self, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute the facts agent workflow.
        
        Args:
            context: The agent context containing the content brief
            
        Returns:
            Facts and figures for content
        """
        # Use the context passed or the agent's own context
        context = context or self.context
        
        logger.info("Gathering facts and figures")
        
        # For this simplified version, we'll just call the parent run method
        # with a structured prompt about gathering facts
        response = await super().run(
            user_message=f"""
            Based on the content brief for the keyword: {context.get('keyword', 'unknown')}, 
            gather relevant facts and figures that will enhance the content.
            
            Include:
            1. Recent statistics
            2. Expert quotes or studies
            3. Industry trends
            4. Authoritative sources
            
            Format the response as JSON.
            """,
            use_json_mode=True
        )
        
        # Add to context for other agents to use
        if context is not self.context:
            context["facts_output"] = response
        else:
            self.add_context({"facts_output": response})
        
        return response
