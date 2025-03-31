#!/usr/bin/env python3
"""
Mini test for Content Creation Team with shortened responses
This is designed to test the system with minimal token usage by:
1. Running each agent individually like in the working integration test
2. Limiting max tokens for all responses
3. Using shorter test prompts
"""

import os
import sys
import logging
import json
import datetime
import re
from dotenv import load_dotenv

# Add parent directory to path so we can import the content_creation_team module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from content_creation_team import create_facts_prompt, extract_gap_analysis

# Import Agno components directly
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
logger = logging.getLogger("mini_test")

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

def test_run_mini_agents():
    """Run a minimal test using individual agents with the run() method
    
    This test is designed to use minimal tokens while still testing the full
    system integration. It uses:
    - Shorter prompts
    - Lower max_tokens in model calls
    - A simple topic that doesn't require extensive research
    """
    try:
        # Check API keys
        if not check_api_keys():
            logger.error("Missing API keys. Please set all required API keys in .env file.")
            return
        
        logger.info("Running mini test with individual agents")
        
        # Get API keys
        openai_api_key = os.getenv("OPENAI_API_KEY")
        anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        xai_api_key = os.getenv("XAI_API_KEY")
        
        # Simple topic that won't require extensive research
        topic = "desk organization mini test"
        logger.info(f"Starting mini test with topic: {topic}")
        
        # Step 1: Research with O3Mini (shortened)
        logger.info("Step 1: Running Research Engine (O3Mini)")
        research_agent = Agent(
            name="Research Engine",
            model=OpenAIChat(id="gpt-3.5-turbo-1106", api_key=openai_api_key, max_tokens=300),
            tools=[DuckDuckGoTools()],
        )
        
        research_prompt = f"Analyze content structure and trends for '{topic}' in 200 words or less"
        research_output = research_agent.run(research_prompt)
        logger.info(f"Research output received ({len(research_output.content)} chars)")
        
        # Step 2: Brief creation with DeepSeek (shortened)
        logger.info("Step 2: Running Brief Creator (DeepSeek)")
        brief_agent = Agent(
            name="Brief Creator",
            model=DeepSeek(id="deepseek-chat", api_key=deepseek_api_key),
        )
        
        brief_prompt = f"""
        You are a content strategy specialist. Based on the following research, create a brief content outline 
        with a focus on identifying content gaps:
        
        {research_output.content}
        
        Include a section clearly labeled "Gap Analysis" that identifies 2-3 content opportunities 
        competitors are missing. Keep your response under 300 words.
        """
        
        brief_output = brief_agent.run(brief_prompt)
        logger.info(f"Brief output received ({len(brief_output.content)} chars)")
        
        # Extract gap analysis for facts collection
        gap_analysis = extract_gap_analysis(brief_output.content)
        logger.info(f"Gap Analysis extracted ({len(gap_analysis)} chars)")
        
        # Step 3: Facts collection with Grok (shortened)
        logger.info("Step 3: Running Facts Collector (Grok/xAI)")
        
        # Create a structured prompt for Grok
        facts_prompt = create_facts_prompt(topic, gap_analysis)
        
        facts_agent = Agent(
            name="Facts Collector",
            model=xAI(id="grok-beta", api_key=xai_api_key, base_url="https://api.x.ai/v1"),
            tools=[DuckDuckGoTools()],
        )
        
        # Add a length constraint to the prompt
        facts_prompt += "\n\nKeep your response concise, with 3-5 stats and 2-3 social insights at most."
        
        facts_output = facts_agent.run(facts_prompt)
        logger.info(f"Facts output received ({len(facts_output.content)} chars)")
        
        # Step 4: Content creation with Claude (shortened)
        logger.info("Step 4: Running Content Creator (Claude)")
        
        content_agent = Agent(
            name="Content Creator",
            model=Claude(id="claude-3-sonnet-20240229", api_key=anthropic_api_key, max_tokens=500),
        )
        
        content_prompt = f"""
        Create a 150-word outline about {topic} based on:
        
        RESEARCH:
        {research_output.content[:1000]}...
        
        CONTENT BRIEF:
        {brief_output.content[:1000]}...
        
        FACTS AND STATISTICS:
        {facts_output.content[:1000]}...
        
        The content should be concise and practical. Focus on an outline only.
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
                    "output": facts_output.content
                },
                "content": {
                    "prompt": content_prompt,
                    "output": content_output.content
                }
            }
        }
        
        # Save results to a file
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"mini_test_results_{timestamp}.json"
        
        with open(filename, "w") as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Mini test results saved to {filename}")
        return results
    
    except Exception as e:
        logger.exception(f"Error in mini test: {str(e)}")
        return None

def test_gap_analysis_extraction():
    """Test the gap analysis extraction function with various inputs"""
    test_cases = [
        # Case 1: Standard format with heading
        """
        # Introduction
        This is the introduction.
        
        # Gap Analysis
        This is the gap analysis content.
        There are multiple lines.
        
        # Conclusion
        This is the conclusion.
        """,
        
        # Case 2: With "Gap Analysis:" format
        """
        Introduction:
        This is the introduction.
        
        Gap Analysis:
        This is the gap analysis content.
        There are multiple lines.
        
        Conclusion:
        This is the conclusion.
        """,
        
        # Case 3: Just sentences with gap keywords
        """
        This is a brief without clear sections.
        There is a significant gap in coverage around mobile optimization.
        Competitors have missed opportunities in addressing user questions.
        The market is underserved when it comes to practical examples.
        """
    ]
    
    logger.info("Testing gap analysis extraction...")
    
    for i, test_case in enumerate(test_cases):
        logger.info(f"Test case {i+1}:")
        extracted = extract_gap_analysis(test_case)
        logger.info(f"Extracted ({len(extracted)} chars): {extracted[:100]}...")
    
    logger.info("Gap analysis extraction tests complete")

if __name__ == "__main__":
    print("Running mini tests for content creation pipeline")
    print("-----------------------------------------------")
    
    # Test gap analysis extraction
    test_gap_analysis_extraction()
    
    # Run mini agent test - this matches the approach in test_integration_agno.py
    results = test_run_mini_agents()
    
    if results:
        print("\nMini test completed successfully!")
    else:
        print("\nMini test failed.") 