#!/usr/bin/env python3
"""
Integration test for the Content Creation Team using Agno for all stages
with explicit API key passing
"""

import os
import logging
import json
import datetime
import re
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
logger = logging.getLogger("integration_test")

def get_formatted_date():
    """Get current date formatted as Month Day, Year"""
    return datetime.datetime.now().strftime("%B %d, %Y")

def create_facts_prompt(topic, gap_analysis=None):
    """Create a structured system prompt for fetching real-time facts
    
    Args:
        topic (str): The topic to research
        gap_analysis (str, optional): Gap analysis from previous agent
        
    Returns:
        str: Formatted system prompt
    """
    current_date = get_formatted_date()
    
    prompt = f"""Fetch real-time data as of {current_date}, related to '{topic}' for an SEO-optimized blog. Include:
1. The latest statistics or facts from credible web sources (e.g., travel reports, news articles, industry blogs).
2. Trending discussions or insights from X posts, YouTube videos/comments, Reddit threads, Hacker News posts, and other relevant social platforms (e.g., hashtags, sentiments, key topics).
3. A concise summary linking the data to the keyword and suggesting how it can enhance SEO relevance.
"""

    # Add gap analysis if provided
    if gap_analysis:
        prompt += f"""If a content gap analysis is provided below, incorporate it to identify unique angles or underserved topics competitors may have missed. 

---BEGIN GAP ANALYSIS---
{gap_analysis}
---END GAP ANALYSIS---
"""

    prompt += """Return the response in JSON format with fields: 'stats' (list of facts with sources and dates), 'social_insights' (list of trends with platform, sentiment, and examples), and 'summary' (text tying it to the keyword and SEO goals)."""

    return prompt

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

def run_integration_test_agno(topic):
    """Run integration test using Agno for all stages with explicit API keys
    
    Args:
        topic (str): The topic to create content about
    """
    logger.info(f"Starting integration test for topic: {topic}")
    
    # Get API keys
    openai_api_key = os.getenv("OPENAI_API_KEY")
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
    xai_api_key = os.getenv("XAI_API_KEY")
    
    # Step 1: Research with O3Mini
    logger.info("Step 1: Running Research Engine (O3Mini)")
    research_agent = Agent(
        name="Research Engine",
        model=OpenAIChat(id="gpt-3.5-turbo-1106", api_key=openai_api_key),
        tools=[DuckDuckGoTools()],
    )
    
    research_prompt = f"Analyze content structure and trends for '{topic}'"
    research_output = research_agent.run(research_prompt)
    logger.info(f"Research output received ({len(research_output.content)} chars)")
    
    # Step 2: Brief creation with DeepSeek
    logger.info("Step 2: Running Brief Creator (DeepSeek)")
    brief_agent = Agent(
        name="Brief Creator",
        model=DeepSeek(id="deepseek-chat", api_key=deepseek_api_key),
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
    
    # Create a structured prompt for Grok
    facts_prompt = create_facts_prompt(topic, gap_analysis)
    
    facts_agent = Agent(
        name="Facts Collector",
        model=xAI(id="grok-beta", api_key=xai_api_key, base_url="https://api.x.ai/v1"),
        tools=[DuckDuckGoTools()],
    )
    
    facts_output = facts_agent.run(facts_prompt)
    logger.info(f"Facts output received ({len(facts_output.content)} chars)")
    
    # Step 4: Content creation with Claude
    logger.info("Step 4: Running Content Creator (Claude)")
    
    content_agent = Agent(
        name="Content Creator",
        model=Claude(id="claude-3-sonnet-20240229", api_key=anthropic_api_key),
    )
    
    content_prompt = f"""
    Create a 500-word {topic} article based on:
    
    RESEARCH:
    {research_output.content[:2000]}...
    
    CONTENT BRIEF:
    {brief_output.content[:2000]}...
    
    FACTS AND STATISTICS:
    {facts_output.content[:2000]}...
    
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
    filename = f"integration_test_results_agno_{timestamp}.json"
    
    with open(filename, "w") as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Integration test results saved to {filename}")
    
    return results

if __name__ == "__main__":
    if not check_api_keys():
        logger.error("Missing API keys. Please set all required API keys in .env file.")
        exit(1)
    
    # Run test with a suitable topic
    results = run_integration_test_agno("sustainable travel trends 2025")
    
    if results:
        logger.info("Integration test completed successfully!")
    else:
        logger.error("Integration test failed.") 