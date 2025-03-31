import os
import json
from datetime import datetime
from dotenv import load_dotenv
import logging

# Agno imports
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.models.anthropic import Claude
from agno.models.deepseek import DeepSeek
from agno.models.xai import xAI

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("agno_token_usage")

# Load environment variables
load_dotenv()

def run_demo():
    """Run a simple demonstration of Agno's built-in token tracking."""
    logger.info("Testing Agno's built-in token tracking")
    
    # Create and run an OpenAI agent
    openai_agent = Agent(
        name="OpenAI Agent",
        model=OpenAIChat(id="gpt-3.5-turbo"),
        markdown=True,
        show_tool_calls=True,
        debug_mode=True  # Enable detailed logging
    )
    
    # Run the agent with a simple prompt
    response = openai_agent.run("Write a short paragraph about sustainable travel.")
    
    # The token usage is available in the telemetry data
    # Agno logs this data automatically, but we can also print it ourselves
    logger.info(f"Agent response: {response[:100]}...")
    
    # Save the results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results = {
        "timestamp": timestamp,
        "response": response,
        "notes": "Token usage is automatically tracked by Agno's telemetry system"
    }
    
    with open(f"agno_usage_demo_{timestamp}.json", "w") as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Results saved to agno_usage_demo_{timestamp}.json")
    logger.info("Check the logs for telemetry data, which includes token usage information")
    logger.info("For detailed token usage, check Agno's telemetry database or logs")

if __name__ == "__main__":
    run_demo() 