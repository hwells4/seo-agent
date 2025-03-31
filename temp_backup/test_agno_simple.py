#!/usr/bin/env python3
"""
Simplified linear test script for Agno Team based on documentation examples.
No async/await needed for basic testing.
"""

import logging
import sys
import os
from textwrap import dedent
from dotenv import load_dotenv

from agno.agent import Agent
from agno.team import Team
from agno.models.openai import OpenAIChat
from agno.storage.json import JsonStorage

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger("agno_test")

def main():
    """Test Agno Team with minimal linear configuration based on documentation."""
    logger.info("Starting Simple Agno Team test")
    
    # Set OpenAI API key from environment
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")
    logger.info(f"API Key set: {'OPENAI_API_KEY' in os.environ}")
    
    try:
        # Create storage
        storage = JsonStorage(dir_path="./test_storage")
        logger.info("Created storage")
        
        # Create simple agents - no custom implementation needed
        agent1 = Agent(
            name="Agent1",
            role="First test agent",
            model=OpenAIChat(id="gpt-3.5-turbo-1106"),
            storage=storage,
            instructions=dedent("""
            You are Agent1, a helpful assistant.
            Respond to all queries with useful information.
            Keep your responses concise and clear.
            """),
        )
        
        agent2 = Agent(
            name="Agent2",
            role="Second test agent",
            model=OpenAIChat(id="gpt-3.5-turbo-1106"),
            storage=storage,
            instructions=dedent("""
            You are Agent2, a helpful assistant.
            Respond to all queries with useful information.
            Always provide a different perspective from other agents.
            """),
        )
        
        logger.info("Created test agents")
        
        # Create team with coordinate mode
        team = Team(
            name="Test Team",
            mode="coordinate",  # Use coordinate mode for linear processing
            model=OpenAIChat(id="gpt-3.5-turbo-1106"),
            members=[agent1, agent2],
            storage=storage,
            instructions=[
                "You are a team coordinator.",
                "Break down tasks and delegate to appropriate team members.",
                "Synthesize responses into a cohesive answer."
            ],
            success_criteria="Task has been completed with input from all relevant team members.",
            debug_mode=True,  # Enable debugging
            show_members_responses=True
        )
        
        logger.info("Created team")
        
        # Run team with non-async method
        logger.info("Running team...")
        response = team.run(message="What's the capital of France?")
        
        logger.info(f"Team run completed with response: {response}")
        
    except Exception as e:
        logger.error(f"Error in test: {e}", exc_info=True)

if __name__ == "__main__":
    main() 