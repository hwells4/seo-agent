#!/usr/bin/env python3
"""
Debug script to test environment variables and Agno model configuration
"""

import os
import logging
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("env_debug")

# Load environment variables
load_dotenv()

# Print API keys for debugging
logger.info(f"OPENAI_API_KEY exists: {bool(os.getenv('OPENAI_API_KEY'))}")
logger.info(f"ANTHROPIC_API_KEY exists: {bool(os.getenv('ANTHROPIC_API_KEY'))}")
logger.info(f"DEEPSEEK_API_KEY exists: {bool(os.getenv('DEEPSEEK_API_KEY'))}")
logger.info(f"XAI_API_KEY exists: {bool(os.getenv('XAI_API_KEY'))}")

# Print the first few characters of each key for verification
if os.getenv('OPENAI_API_KEY'):
    logger.info(f"OPENAI_API_KEY starts with: {os.getenv('OPENAI_API_KEY')[:10]}...")
if os.getenv('ANTHROPIC_API_KEY'):
    logger.info(f"ANTHROPIC_API_KEY starts with: {os.getenv('ANTHROPIC_API_KEY')[:10]}...")
if os.getenv('DEEPSEEK_API_KEY'):
    logger.info(f"DEEPSEEK_API_KEY starts with: {os.getenv('DEEPSEEK_API_KEY')[:10]}...")
if os.getenv('XAI_API_KEY'):
    logger.info(f"XAI_API_KEY starts with: {os.getenv('XAI_API_KEY')[:10]}...")

# Try importing and inspecting the Agno models
try:
    from agno.models.deepseek import DeepSeek
    from agno.models.xai import xAI
    
    # Create model instances
    deepseek_model = DeepSeek()
    xai_model = xAI()
    
    # Print model configurations
    logger.info(f"DeepSeek model config: id={deepseek_model.id}, api_key exists: {bool(deepseek_model.api_key)}")
    if deepseek_model.api_key:
        logger.info(f"DeepSeek API key starts with: {deepseek_model.api_key[:10]}...")
    logger.info(f"DeepSeek base_url: {deepseek_model.base_url}")
    
    logger.info(f"xAI model config: id={xai_model.id}, api_key exists: {bool(xai_model.api_key)}")
    if xai_model.api_key:
        logger.info(f"xAI API key starts with: {xai_model.api_key[:10]}...")
    logger.info(f"xAI base_url: {xai_model.base_url}")
    
except ImportError as e:
    logger.error(f"Error importing Agno models: {str(e)}")
except Exception as e:
    logger.error(f"Error creating model instances: {str(e)}")

# Print all environment variables for debugging
logger.debug("--- All Environment Variables ---")
for key, value in os.environ.items():
    if 'KEY' in key and len(value) > 5:  # Only print API keys and mask them
        logger.debug(f"{key}: {value[:5]}...{value[-2:]}")
    elif 'TOKEN' in key and len(value) > 5:
        logger.debug(f"{key}: {value[:5]}...{value[-2:]}")
    
logger.info("Environment debug complete") 