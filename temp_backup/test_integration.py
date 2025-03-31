#!/usr/bin/env python3
"""
Integration test for the Content Creation Team that verifies:
1. Each model runs properly
2. Each agent uses the results of the previous agent
3. Grok uses real-time data with the gap analysis from DeepSeek
"""

import os
import logging
import json
import datetime
from dotenv import load_dotenv

from content_creation_team import create_content_team, create_facts_prompt
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.models.deepseek import DeepSeek
from agno.models.xai import xAI
from agno.models.anthropic import Claude
from agno.tools.duckduckgo import DuckDuckGoTools
from test_grok_realtime import test_with_real_gap_analysis

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("integration_test")

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

def run_step_by_step_integration_test(topic):
    """Run the integration test step by step and save intermediate results
    
    Args:
        topic (str): The topic to create content about
    """
    logger.info(f"Starting step-by-step integration test for topic: {topic}")
    
    # Step 1: Research with O3Mini
    logger.info("Step 1: Running Research Engine (O3Mini)")
    research_agent = Agent(
        name="Research Engine",
        model=OpenAIChat(id="gpt-3.5-turbo-1106"),
        tools=[DuckDuckGoTools()],
    )
    
    research_prompt = f"Analyze content structure and trends for '{topic}'"
    research_output = research_agent.run(research_prompt)
    logger.info(f"Research output received ({len(research_output.content)} chars)")
    
    # Step 2: Brief creation with DeepSeek
    logger.info("Step 2: Running Brief Creator (DeepSeek)")
    brief_agent = Agent(
        name="Brief Creator",
        model=DeepSeek(id="deepseek-reasoner"),
    )
    
    brief_prompt = f"""
    You are a content strategy specialist. Based on the following research, create a detailed content brief 
    with a strong focus on identifying content gaps and opportunities:
    
    {research_output.content}
    
    Include a section clearly labeled "Gap Analysis" that identifies specific content opportunities 
    competitors are missing or underserving.
    """
    
    brief_output = brief_agent.run(brief_prompt)
    logger.info(f"Brief output received ({len(brief_output.content)} chars)")
    
    # Extract gap analysis for facts collection
    gap_analysis = None
    gap_section_pattern = r"(?i)(?:^|\n)#+\s*Gap Analysis\s*(?:\n|$)(.*?)(?=(?:^|\n)#+\s*|\Z)"
    import re
    match = re.search(gap_section_pattern, brief_output.content, re.DOTALL | re.MULTILINE)
    
    if match:
        gap_analysis = match.group(1).strip()
        logger.info(f"Gap Analysis extracted ({len(gap_analysis)} chars)")
    else:
        # Try more lenient extraction
        gap_pattern = r"(?i)Gap Analysis:?\s*(.*?)(?:\n\n|\n#|\Z)"
        match = re.search(gap_pattern, brief_output.content, re.DOTALL)
        if match:
            gap_analysis = match.group(1).strip()
            logger.info(f"Gap Analysis extracted with fallback method ({len(gap_analysis)} chars)")
        else:
            logger.warning("No Gap Analysis section found. Using generic extraction.")
            # Try to find any mentions of gaps or opportunities
            sentences = re.findall(r'[^.!?]*(?:gap|opportunity|missing|underserved)[^.!?]*[.!?]', brief_output.content, re.IGNORECASE)
            if sentences:
                gap_analysis = " ".join(sentences)
                logger.info(f"Generic gap analysis extracted ({len(gap_analysis)} chars)")
            else:
                gap_analysis = "No specific gap analysis found. Focus on gathering current facts and trends."
                logger.warning("Using default gap analysis")
    
    # Step 3: Facts collection with Grok
    logger.info("Step 3: Running Facts Collector (Grok/xAI)")
    
    # Create a structured prompt using the helper function
    facts_prompt = create_facts_prompt(topic, gap_analysis)
    logger.info(f"Created structured facts prompt with dynamic date and gap analysis")
    
    # Setup the agent with proper tools and model
    facts_agent = Agent(
        name="Facts Collector",
        model=xAI(id="grok-beta"),
        tools=[DuckDuckGoTools()]
    )
    
    # Run the agent with the structured prompt
    try:
        facts_response = facts_agent.run(facts_prompt)
        logger.info(f"Facts output received ({len(facts_response.content)} chars)")
        facts_output = facts_response.content
        
        # Save the prompt and response for inspection
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        facts_filename = f"facts_test_{timestamp}.json"
        
        with open(facts_filename, "w") as f:
            json.dump({
                "topic": topic,
                "prompt": facts_prompt,
                "gap_analysis": gap_analysis,
                "response": facts_output
            }, f, indent=2)
        
        logger.info(f"Facts collection details saved to {facts_filename}")
        
    except Exception as e:
        logger.error(f"Facts collection failed: {str(e)}")
        return None
    
    # Step 4: Content creation with Claude
    logger.info("Step 4: Running Content Creator (Claude)")
    content_agent = Agent(
        name="Content Creator",
        model=Claude(id="claude-3-sonnet-20240229"),
    )
    
    content_prompt = f"""
    Create a 500-word {topic} article based on:
    
    RESEARCH:
    {research_output.content[:2000]}...
    
    CONTENT BRIEF:
    {brief_output.content[:2000]}...
    
    FACTS AND STATISTICS:
    {facts_output[:2000]}...
    
    The content should be helpful, practical, and engaging.
    """
    
    content_output = content_agent.run(content_prompt)
    logger.info(f"Content output received ({len(content_output.content)} chars)")
    
    # Save all steps to a file
    results = {
        "topic": topic,
        "steps": {
            "research": {
                "prompt": research_prompt,
                "output": research_output.content
            },
            "brief": {
                "prompt": brief_prompt,
                "output": brief_output.content,
                "extracted_gap_analysis": gap_analysis
            },
            "facts": {
                "prompt": facts_prompt,
                "output": facts_output
            },
            "content": {
                "prompt": content_prompt,
                "output": content_output.content
            }
        }
    }
    
    # Save to file
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"integration_test_results_{timestamp}.json"
    
    with open(filename, "w") as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Integration test results saved to {filename}")
    
    return results

def run_full_team_test(topic):
    """Run the full team test using the coordinated workflow
    
    Args:
        topic (str): The topic to create content about
    """
    logger.info(f"Starting full team test for topic: {topic}")
    
    # Create and run the team
    team = create_content_team()
    
    prompt = f"Create a blog post about {topic}. The content should be helpful, practical, and about 500 words."
    
    # Run with print_response to see all steps in the console
    logger.info("Running team with coordination...")
    result = team.print_response(message=prompt, stream=True, stream_intermediate_steps=True)
    
    logger.info("Team test completed")
    
    return result

if __name__ == "__main__":
    logger.info("Starting integration tests")
    
    if not check_api_keys():
        logger.error("Missing API keys. Please set all required API keys in .env file.")
        exit(1)
    
    # Topic for testing
    test_topic = "sustainable travel tips"
    
    # Run step-by-step test
    logger.info("\n=== Running Step-by-Step Integration Test ===")
    step_by_step_results = run_step_by_step_integration_test(test_topic)
    
    # Run full team test
    logger.info("\n=== Running Full Team Test ===")
    full_team_result = run_full_team_test(test_topic)
    
    logger.info("All integration tests completed") 