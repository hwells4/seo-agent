#!/usr/bin/env python3
"""
Test script to verify the token tracking functionality across all models
"""

import os
import sys
import logging
import json
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("token_tracking_test")

# Add the parent directory to the path to import agents modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import token tracker to measure usage
from agents.utils.token_tracker import token_tracker

# Import Agno components
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.models.anthropic import Claude
from agno.models.deepseek import DeepSeek
from agno.models.xai import xAI
from agno.tools.duckduckgo import DuckDuckGoTools

# Load environment variables
load_dotenv()

# Ensure test_storage directory exists
os.makedirs("test_storage", exist_ok=True)

def check_api_keys():
    """Check if required API keys are set"""
    missing_keys = []
    
    if not os.getenv("OPENAI_API_KEY"):
        missing_keys.append("OPENAI_API_KEY")
    
    if not os.getenv("ANTHROPIC_API_KEY"):
        missing_keys.append("ANTHROPIC_API_KEY")
    
    if not os.getenv("DEEPSEEK_API_KEY"):
        missing_keys.append("DEEPSEEK_API_KEY")
    
    if not os.getenv("XAI_API_KEY"):
        missing_keys.append("XAI_API_KEY")
    
    if missing_keys:
        logger.error(f"Missing API keys: {', '.join(missing_keys)}")
        return False
    
    return True

def test_openai_tracking():
    """Test token tracking with OpenAI models"""
    logger.info("Testing token tracking with OpenAI models")
    
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        logger.error("OPENAI_API_KEY environment variable is not set")
        return False
    
    try:
        # Create a test agent with OpenAI
        agent = Agent(
            name="OpenAITester",
            model=OpenAIChat(id="gpt-3.5-turbo", api_key=openai_api_key),
            instructions="You are a helpful assistant. Provide concise answers."
        )
        
        # Run a simple query
        prompt = "Explain the concept of token tracking in LLMs in one sentence."
        logger.info(f"Running OpenAI test with prompt: '{prompt}'")
        
        response = agent.run(prompt)
        content = response.content if hasattr(response, 'content') else str(response)
        
        # Track token usage
        token_tracker.track_step(
            step_name="openai_test",
            provider="openai",
            model="gpt-3.5-turbo",
            input_text=prompt,
            output_text=content
        )
        
        # Save response
        with open("test_storage/openai_test_response.txt", "w") as f:
            f.write(content)
        
        logger.info(f"OpenAI test response ({len(content)} chars): {content}")
        logger.info("Response saved to test_storage/openai_test_response.txt")
        return True
    
    except Exception as e:
        logger.error(f"Error testing OpenAI tracking: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def test_anthropic_tracking():
    """Test token tracking with Anthropic models"""
    logger.info("Testing token tracking with Anthropic models")
    
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    if not anthropic_api_key:
        logger.error("ANTHROPIC_API_KEY environment variable is not set")
        return False
    
    try:
        # Create a test agent with Anthropic
        agent = Agent(
            name="AnthropicTester",
            model=Claude(id="claude-3-sonnet-20240229", api_key=anthropic_api_key),
            instructions="You are a helpful assistant. Provide concise answers."
        )
        
        # Run a simple query
        prompt = "Explain the concept of token pricing in LLMs in one sentence."
        logger.info(f"Running Anthropic test with prompt: '{prompt}'")
        
        response = agent.run(prompt)
        content = response.content if hasattr(response, 'content') else str(response)
        
        # Track token usage
        token_tracker.track_step(
            step_name="anthropic_test",
            provider="anthropic",
            model="claude-3-sonnet-20240229",
            input_text=prompt,
            output_text=content
        )
        
        # Save response
        with open("test_storage/anthropic_test_response.txt", "w") as f:
            f.write(content)
        
        logger.info(f"Anthropic test response ({len(content)} chars): {content}")
        logger.info("Response saved to test_storage/anthropic_test_response.txt")
        return True
    
    except Exception as e:
        logger.error(f"Error testing Anthropic tracking: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def test_deepseek_tracking():
    """Test token tracking with DeepSeek models"""
    logger.info("Testing token tracking with DeepSeek models")
    
    deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
    if not deepseek_api_key:
        logger.error("DEEPSEEK_API_KEY environment variable is not set")
        return False
    
    try:
        # Create a test agent with DeepSeek
        agent = Agent(
            name="DeepSeekTester",
            model=DeepSeek(id="deepseek-chat", api_key=deepseek_api_key),
            instructions="You are a helpful assistant. Provide concise answers."
        )
        
        # Run a simple query
        prompt = "Explain the concept of token estimation in LLMs in one sentence."
        logger.info(f"Running DeepSeek test with prompt: '{prompt}'")
        
        response = agent.run(prompt)
        content = response.content if hasattr(response, 'content') else str(response)
        
        # Track token usage
        token_tracker.track_step(
            step_name="deepseek_test",
            provider="deepseek",
            model="deepseek-chat",
            input_text=prompt,
            output_text=content
        )
        
        # Save response
        with open("test_storage/deepseek_test_response.txt", "w") as f:
            f.write(content)
        
        logger.info(f"DeepSeek test response ({len(content)} chars): {content}")
        logger.info("Response saved to test_storage/deepseek_test_response.txt")
        return True
    
    except Exception as e:
        logger.error(f"Error testing DeepSeek tracking: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def test_xai_tracking():
    """Test token tracking with xAI models"""
    logger.info("Testing token tracking with xAI models")
    
    xai_api_key = os.getenv("XAI_API_KEY")
    if not xai_api_key:
        logger.error("XAI_API_KEY environment variable is not set")
        return False
    
    try:
        # Create a test agent with xAI
        agent = Agent(
            name="xAITester",
            model=xAI(id="grok-beta", api_key=xai_api_key, base_url="https://api.x.ai/v1"),
            instructions="You are a helpful assistant. Provide concise answers."
        )
        
        # Run a simple query
        prompt = "Explain the concept of cost calculation in LLMs in one sentence."
        logger.info(f"Running xAI test with prompt: '{prompt}'")
        
        response = agent.run(prompt)
        content = response.content if hasattr(response, 'content') else str(response)
        
        # Track token usage
        token_tracker.track_step(
            step_name="xai_test",
            provider="xai",
            model="grok-beta",
            input_text=prompt,
            output_text=content
        )
        
        # Save response
        with open("test_storage/xai_test_response.txt", "w") as f:
            f.write(content)
        
        logger.info(f"xAI test response ({len(content)} chars): {content}")
        logger.info("Response saved to test_storage/xai_test_response.txt")
        return True
    
    except Exception as e:
        logger.error(f"Error testing xAI tracking: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def main():
    """Main function to run all token tracking tests"""
    # Reset token tracker
    token_tracker.reset()
    
    # Check API keys
    if not check_api_keys():
        logger.error("Missing API keys. Cannot run all tests.")
        return 1
    
    # Run tests for each model provider
    results = {
        "openai": test_openai_tracking(),
        "anthropic": test_anthropic_tracking(),
        "deepseek": test_deepseek_tracking(),
        "xai": test_xai_tracking()
    }
    
    # Print token usage report
    token_tracker.print_usage_report()
    
    # Save token usage report
    report_file = token_tracker.save_report_to_file("test_storage/token_tracking_test_usage.json")
    logger.info(f"Token usage report saved to {report_file}")
    
    # Save summary report
    summary = {
        "test_results": results,
        "all_passed": all(results.values()),
        "timestamp": str(token_tracker.last_tracked)
    }
    
    with open("test_storage/token_tracking_test_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    logger.info("Test summary saved to test_storage/token_tracking_test_summary.json")
    
    # Show test results
    print("\n===== TOKEN TRACKING TEST RESULTS =====")
    for provider, success in results.items():
        status = "SUCCESS" if success else "FAILED"
        print(f"{provider.upper()}: {status}")
    print("======================================\n")
    
    # Return success if all tests passed
    if all(results.values()):
        logger.info("All token tracking tests completed successfully")
        return 0
    else:
        logger.error("Some token tracking tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 