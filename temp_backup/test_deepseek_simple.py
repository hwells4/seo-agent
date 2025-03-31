#!/usr/bin/env python3
"""
Minimal test for DeepSeek model with Agno
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
logger = logging.getLogger("deepseek_simple")

# Verify API key
deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
if not deepseek_api_key:
    logger.error("DEEPSEEK_API_KEY not found in environment variables")
    exit(1)

logger.info(f"Using DeepSeek API key: {deepseek_api_key[:10]}...")

try:
    # Import Agno components
    from agno.agent import Agent
    from agno.models.deepseek import DeepSeek
    
    # Create a simple agent with DeepSeek
    agent = Agent(
        name="DeepSeek Simple Test",
        model=DeepSeek(id="deepseek-chat", api_key=deepseek_api_key)  # Explicitly pass the API key
    )
    
    logger.info("Sending a simple prompt to DeepSeek...")
    response = agent.run("Write a short poem about technology")
    
    logger.info(f"DeepSeek response: {response.content}")
    logger.info("Test completed successfully")
    
except Exception as e:
    logger.error(f"Error: {str(e)}")
    import traceback
    logger.error(traceback.format_exc()) 