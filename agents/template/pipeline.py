#!/usr/bin/env python3
"""
Template Agent Pipeline - Use this as a starting point for new agent pipelines.
Copy this directory and customize it for your specific use case.
"""

import os
import logging
import datetime
import json
from textwrap import dedent
from dotenv import load_dotenv

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.models.anthropic import Claude
from agno.storage.json import JsonStorage
from agno.tools.duckduckgo import DuckDuckGoTools

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("agent_template")

def check_api_keys():
    """Check if required API keys are set"""
    missing_keys = []
    
    if not os.getenv("OPENAI_API_KEY"):
        missing_keys.append("OPENAI_API_KEY")
    
    if not os.getenv("ANTHROPIC_API_KEY"):
        missing_keys.append("ANTHROPIC_API_KEY")
    
    if missing_keys:
        logger.error(f"Missing API keys: {', '.join(missing_keys)}")
        return False
    
    return True

def create_agents():
    """Create the pipeline agents.
    
    Returns:
        tuple: Created agents ready to use
    """
    # Check API keys first
    if not check_api_keys():
        logger.error("Missing API keys. Please set all required API keys in the .env file.")
        raise ValueError("Missing API keys for one or more required services")
    
    # Get API keys
    openai_api_key = os.getenv("OPENAI_API_KEY")
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    
    # Create storage
    storage = JsonStorage(dir_path="./template_storage")
    
    # Example agent 1
    agent1 = Agent(
        name="First Agent",
        role="Describe the role of this agent",
        model=OpenAIChat(id="gpt-3.5-turbo", api_key=openai_api_key),
        storage=storage,
        tools=[DuckDuckGoTools()],
        instructions=dedent("""
            You are an expert at your specific task.
            
            When given input:
            1. Process it carefully
            2. Produce high-quality output
            
            Your output should meet these criteria:
            - Criterion 1
            - Criterion 2
            - Criterion 3
        """),
    )
    
    # Example agent 2
    agent2 = Agent(
        name="Second Agent",
        role="Describe the role of this agent",
        model=Claude(id="claude-3-sonnet-20240229", api_key=anthropic_api_key),
        storage=storage,
        instructions=dedent("""
            You are an expert at your specific task.
            
            When given input:
            1. Process it carefully
            2. Produce high-quality output
            
            Your output should meet these criteria:
            - Criterion 1
            - Criterion 2
            - Criterion 3
        """),
    )
    
    logger.info("Agents initialized")
    return (agent1, agent2)

def run_pipeline(input_text, options=None, save_results=True):
    """Run the agent pipeline.
    
    Args:
        input_text (str): The main input for the pipeline
        options (dict, optional): Additional options for customizing the pipeline
        save_results (bool, optional): Whether to save the results to a JSON file
        
    Returns:
        dict: Results of the pipeline
    """
    logger.info(f"Starting pipeline for input: {input_text[:50]}...")
    
    # Initialize agents
    agent1, agent2 = create_agents()
    
    results = {
        "input": input_text,
        "steps": {}
    }
    
    # Step 1: First agent
    logger.info("Step 1: Running first agent")
    prompt1 = f"Process this input: {input_text}"
    response1 = agent1.run(prompt1)
    result1 = response1.content if hasattr(response1, 'content') else str(response1)
    results["steps"]["agent1"] = {
        "prompt": prompt1,
        "output": result1
    }
    logger.info(f"First agent output received ({len(result1)} chars)")
    
    # Step 2: Second agent
    logger.info("Step 2: Running second agent")
    prompt2 = f"""
        Process the following input based on previous processing:
        
        ORIGINAL INPUT:
        {input_text}
        
        PREVIOUS PROCESSING:
        {result1}
    """
    response2 = agent2.run(prompt2)
    result2 = response2.content if hasattr(response2, 'content') else str(response2)
    results["steps"]["agent2"] = {
        "prompt": prompt2,
        "output": result2
    }
    logger.info(f"Second agent output received ({len(result2)} chars)")
    
    # Save results to a file
    if save_results:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"template_results_{timestamp}.json"
        
        with open(filename, "w") as f:
            json.dump(results, f, indent=2)
        logger.info(f"Results saved to {filename}")
    
    logger.info("Pipeline completed")
    return results

def main():
    """Run the pipeline with a test input."""
    try:
        # Check if API keys are available
        if not check_api_keys():
            logger.error("Missing API keys. Please set all required API keys in .env file.")
            return
        
        # Test input
        test_input = "This is a test input for the template pipeline."
        
        # Run the pipeline
        results = run_pipeline(
            input_text=test_input,
            save_results=True
        )
        
        # Print the final result
        print("\n\n" + "=" * 50)
        print("FINAL RESULT:")
        print("=" * 50)
        print(results["steps"]["agent2"]["output"])
        print("=" * 50)
        
    except Exception as e:
        logger.exception(f"Error in pipeline process: {str(e)}")

if __name__ == "__main__":
    main() 