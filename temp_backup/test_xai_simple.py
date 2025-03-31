#!/usr/bin/env python3
"""
Minimal test for xAI/Grok model with Agno
"""

import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("xai_simple")

# Verify API key
xai_api_key = os.getenv("XAI_API_KEY")
if not xai_api_key:
    logger.error("XAI_API_KEY not found in environment variables")
    exit(1)

logger.info(f"Using xAI API key: {xai_api_key[:10]}...")

try:
    # Import Agno components
    from agno.agent import Agent
    from agno.models.xai import xAI
    
    # Create a simple agent with xAI
    agent = Agent(
        name="xAI/Grok Simple Test",
        model=xAI(id="grok-beta", api_key=xai_api_key)  # Explicitly pass the API key
    )
    
    logger.info("Sending a simple prompt to xAI/Grok...")
    response = agent.run("What is the current time in New York?")
    
    logger.info(f"xAI/Grok response: {response.content}")
    logger.info("Test completed successfully")
    
except Exception as e:
    logger.error(f"Error: {str(e)}")
    import traceback
    logger.error(traceback.format_exc()) 