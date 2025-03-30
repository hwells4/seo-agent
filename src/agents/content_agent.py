"""
Content Generation Agent.

This agent transforms research, brief, and facts into polished,
human-sounding content that fulfills identified search intent.
"""

import logging
from typing import Dict, Any, Optional

from agno.agent import Agent
from agno.models.anthropic import Claude  # Updated from AnthropicChat
from agno.storage.base import Storage as StorageProvider

from src.config.settings import settings
from src.config.agno_config import get_knowledge_provider

# Set up logger
logger = logging.getLogger(__name__)


class ContentAgent(Agent):
    """Agent for generating polished, human-sounding content."""

    def __init__(self, storage: Optional[StorageProvider] = None):
        """Initialize the content agent.
        
        Args:
            storage: Optional storage provider for persistent state
        """
        super().__init__(
            name="Content Agent",
            description="Transforms research, brief, and facts into polished, human-sounding content.",
            model=Claude(id="claude-3-7-sonnet-20240307"),  # Updated from AnthropicChat
            storage=storage,
            knowledge=get_knowledge_provider()
        )
    
    async def run(self, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute the content generation workflow.
        
        Args:
            context: The agent context containing research, brief, and facts
            
        Returns:
            Generated content
        """
        # Use the context passed or the agent's own context
        context = context or self.context
        
        logger.info("Generating content")
        
        # Get the research output, content brief, and facts from context
        research = context.get("research_output", {})
        brief = context.get("content_brief", {})
        facts = context.get("facts_output", {})
        keyword = context.get("keyword", "unknown")
        
        # For this simplified version, we'll create a structured prompt
        # that brings together all the inputs
        response = await super().run(
            user_message=f"""
            Create polished, human-sounding content for the keyword: {keyword}.
            
            Use the following inputs:
            
            RESEARCH OUTPUT:
            {research}
            
            CONTENT BRIEF:
            {brief}
            
            FACTS AND FIGURES:
            {facts}
            
            Generate content that:
            1. Fulfills the identified search intent
            2. Covers all topics in the brief
            3. Incorporates the facts and figures provided
            4. Sounds authentically human and engaging
            5. Is structured according to the brief's recommendations
            6. Demonstrates expertise and authoritativeness
            
            The content should include:
            1. An engaging title
            2. A compelling introduction
            3. Well-structured body sections
            4. A strong conclusion
            
            Format the response as a JSON object with the following structure:
            {{
                "title": "Your title here",
                "content_sections": [
                    {{
                        "heading": "Introduction",
                        "content": "Introduction text here"
                    }},
                    ...additional sections
                ],
                "meta_description": "A concise meta description for SEO"
            }}
            """,
            use_json_mode=True
        )
        
        # Add to context
        if context is not self.context:
            context["generated_content"] = response
        else:
            self.add_context({"generated_content": response})
        
        return response
