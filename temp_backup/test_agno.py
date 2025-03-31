#!/usr/bin/env python3
"""
Simple test script to debug Agno Team issues.
"""

import asyncio
import logging
import sys
import os
from typing import Dict, Any, Optional, Iterator
from dotenv import load_dotenv
from uuid import uuid4

from agno.agent import Agent
from agno.team import Team
from agno.models.openai import OpenAIChat
from agno.storage.json import JsonStorage
from agno.run.response import RunResponse

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for more detailed logs
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger("agno_test")

# Create a simple test agent
class TestAgent(Agent):
    """Simple agent for testing."""
    
    def __init__(self, name, storage=None):
        super().__init__(
            name=name,
            description=f"Test agent {name}",
            model=OpenAIChat(id="gpt-3.5-turbo-1106"),  # Using O3Mini for cost-effective testing
            storage=storage
        )
    
    def _run(
        self, 
        message=None, 
        stream=False, 
        **kwargs
    ) -> Iterator[RunResponse]:
        """Override _run method instead of run to work correctly with the Team.
        
        This returns an iterator that yields a single RunResponse.
        """
        logger.info(f"Agent {self.name} _run called with message: {message}, kwargs: {kwargs}")
        
        # Create a proper RunResponse object with content
        content = f"Hello from {self.name}. I processed the request: {message}"
        
        # Add the agent name in the content so we know who processed it
        run_id = str(uuid4())  # Generate a unique run ID
        
        # Create response with only valid parameters
        response = RunResponse(
            content=content,
            run_id=run_id,
            agent_id=self.agent_id,
            session_id=self.session_id
        )
        
        # Add metrics to include information about which agent processed the request
        if response.metrics is None:
            response.metrics = {}
        response.metrics["agent_name"] = self.name
        
        logger.info(f"Agent {self.name} returning response: {response}")
        
        # Yield the response as a single item iterator
        yield response

async def main():
    """Test Agno Team with minimal configuration."""
    logger.info("Starting Agno Team test")
    
    # Set OpenAI API key from environment
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")
    logger.info(f"API Key set: {'OPENAI_API_KEY' in os.environ}")
    
    try:
        # Create storage
        storage = JsonStorage(dir_path="./test_storage")
        logger.info("Created in-memory storage")
        
        # Create test agents
        agent1 = TestAgent("Agent1", storage=storage)
        agent2 = TestAgent("Agent2", storage=storage)
        
        logger.info("Created test agents")
        
        # Create team
        team = Team(
            name="Test Team",
            members=[agent1, agent2],
            storage=storage,
            context={"test_key": "test_value"},
            model=OpenAIChat(id="gpt-3.5-turbo-1106"),  # Add a team model
            debug_mode=True,  # Enable debug mode to see what's happening
            mode="route"  # Use simple route mode instead of coordinate
        )
        
        logger.info("Created team with context")
        
        # Run team
        logger.info("About to run team...")
        result = await team.run(message="Please process this request")
        logger.info(f"Team run completed with result: {result}")
        
    except Exception as e:
        logger.error(f"Error in test: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main()) 