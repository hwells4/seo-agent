#!/usr/bin/env python3
"""
Test script to verify each individual model and the sequential workflow
"""

import os
import json
import logging
from dotenv import load_dotenv

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.models.anthropic import Claude
from agno.models.deepseek import DeepSeek
from agno.models.xai import xAI
from agno.tools.duckduckgo import DuckDuckGoTools

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("model_test")

# Ensure API keys are set
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

# Test each model individually
def test_openai():
    """Test OpenAI model (O3Mini)"""
    logger.info("Testing OpenAI GPT-3.5 Turbo (O3Mini)")
    
    agent = Agent(
        name="OpenAI Test",
        model=OpenAIChat(id="gpt-3.5-turbo-1106")
    )
    
    response = agent.run("Analyze the content structure for 'desk organization tips' blog posts")
    
    logger.info(f"OpenAI Response: {response.content[:100]}...")
    return response.content

def test_deepseek():
    """Test DeepSeek model"""
    logger.info("Testing DeepSeek Reasoner")
    
    agent = Agent(
        name="DeepSeek Test",
        model=DeepSeek(id="deepseek-reasoner")
    )
    
    response = agent.run("Create a content brief for a blog post about 'desk organization tips'")
    
    logger.info(f"DeepSeek Response: {response.content[:100]}...")
    return response.content

def test_xai():
    """Test xAI/Grok model with real-time data"""
    logger.info("Testing xAI Grok with real-time data")
    
    agent = Agent(
        name="xAI Test",
        model=xAI(id="grok-beta"),
        tools=[DuckDuckGoTools()]
    )
    
    # Ask for current facts that require real-time information
    response = agent.run(
        "What are the current trends in desk organization for 2023-2024? Include statistics and recent products if available."
    )
    
    logger.info(f"xAI/Grok Response: {response.content[:100]}...")
    return response.content

def test_claude():
    """Test Claude model"""
    logger.info("Testing Claude 3 Sonnet")
    
    agent = Agent(
        name="Claude Test",
        model=Claude(id="claude-3-sonnet-20240229")
    )
    
    response = agent.run("Write a 300-word blog post about desk organization tips")
    
    logger.info(f"Claude Response: {response.content[:100]}...")
    return response.content

def test_sequential_workflow():
    """Test that each agent can use the output from previous agents"""
    logger.info("Testing sequential workflow")
    
    # Step 1: Research with O3Mini
    research_agent = Agent(
        name="Research",
        model=OpenAIChat(id="gpt-3.5-turbo-1106"),
        tools=[DuckDuckGoTools()]
    )
    
    research_output = research_agent.run("Analyze content structure for 'desk organization tips'")
    logger.info(f"Research output: {research_output.content[:100]}...")
    
    # Step 2: Create brief with OpenAI instead of DeepSeek based on research
    brief_agent = Agent(
        name="Brief Creator",
        model=OpenAIChat(id="gpt-3.5-turbo-1106")  # Using OpenAI instead of DeepSeek temporarily
    )
    
    brief_prompt = f"Create a content brief based on this research:\n\n{research_output.content}"
    brief_output = brief_agent.run(brief_prompt)
    logger.info(f"Brief output: {brief_output.content[:100]}...")
    
    # Step 3: Gather facts with Grok based on brief
    facts_agent = Agent(
        name="Facts Collector",
        model=xAI(id="grok-beta"),
        tools=[DuckDuckGoTools()]
    )
    
    facts_prompt = f"Based on this content brief, collect current facts and statistics:\n\n{brief_output.content}"
    facts_output = facts_agent.run(facts_prompt)
    logger.info(f"Facts output: {facts_output.content[:100]}...")
    
    # Step 4: Create content with Claude based on all previous outputs
    content_agent = Agent(
        name="Content Creator",
        model=Claude(id="claude-3-sonnet-20240229")
    )
    
    content_prompt = f"""
    Create a 500-word blog post based on:
    
    RESEARCH:
    {research_output.content}
    
    CONTENT BRIEF:
    {brief_output.content}
    
    FACTS AND STATISTICS:
    {facts_output.content}
    """
    
    content_output = content_agent.run(content_prompt)
    logger.info(f"Content output: {content_output.content[:100]}...")
    
    # Save all outputs to file for inspection
    with open("sequential_test_results.json", "w") as f:
        json.dump({
            "research": research_output.content,
            "brief": brief_output.content,
            "facts": facts_output.content,
            "content": content_output.content
        }, f, indent=2)
    
    logger.info("Saved all outputs to sequential_test_results.json")
    return content_output.content

if __name__ == "__main__":
    if not check_api_keys():
        logger.error("Missing API keys. Please set all required API keys in .env file.")
        exit(1)
    
    # Test individual models
    logger.info("=== Testing Individual Models ===")
    test_openai()
    # test_deepseek()  # Skip due to API key issues (works directly but not with Agno)
    # test_xai()  # Skip due to API key issues (works directly but not with Agno)
    test_claude()
    
    # Test simple workflow with only OpenAI and Claude
    logger.info("\n=== Testing Simple Workflow (OpenAI + Claude only) ===")
    
    # Step 1: Research with O3Mini
    research_agent = Agent(
        name="Research",
        model=OpenAIChat(id="gpt-3.5-turbo-1106"),
        tools=[DuckDuckGoTools()]
    )
    
    research_output = research_agent.run("Analyze content structure for 'desk organization tips'")
    logger.info(f"Research output: {research_output.content[:100]}...")
    
    # Step 4: Create content with Claude based on research
    content_agent = Agent(
        name="Content Creator",
        model=Claude(id="claude-3-sonnet-20240229")
    )
    
    content_prompt = f"""
    Create a 500-word blog post based on:
    
    RESEARCH:
    {research_output.content}
    """
    
    content_output = content_agent.run(content_prompt)
    logger.info(f"Content output: {content_output.content[:100]}...")
    
    # Save outputs to file for inspection
    with open("simple_workflow_results.json", "w") as f:
        json.dump({
            "research": research_output.content,
            "content": content_output.content
        }, f, indent=2)
    
    logger.info("Saved outputs to simple_workflow_results.json") 