#!/usr/bin/env python3
"""
Integration test for the Content Creation Team that verifies:
1. Each model runs properly using direct API calls where needed
2. Each agent uses the results of the previous agent
"""

import os
import logging
import json
import datetime
from dotenv import load_dotenv
from openai import OpenAI
import anthropic

from agno.agent import Agent
from agno.models.openai import OpenAIChat
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

def run_integration_test_direct(topic):
    """Run integration test using direct API calls where needed
    
    Args:
        topic (str): The topic to create content about
    """
    logger.info(f"Starting integration test for topic: {topic}")
    
    # Step 1: Research with O3Mini via Agno (known to work)
    logger.info("Step 1: Running Research Engine (O3Mini)")
    
    research_agent = Agent(
        name="Research Engine",
        model=OpenAIChat(id="gpt-3.5-turbo-1106"),
        tools=[DuckDuckGoTools()],
    )
    
    research_prompt = f"Analyze content structure and trends for '{topic}'"
    research_output = research_agent.run(research_prompt)
    logger.info(f"Research output received ({len(research_output.content)} chars)")
    
    # Step 2: Brief creation with DeepSeek via direct API
    logger.info("Step 2: Running Brief Creator (DeepSeek) via direct API")
    
    # Get the DeepSeek API key
    deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
    if not deepseek_api_key:
        logger.error("DEEPSEEK_API_KEY not found in environment variables")
        return None
    
    # Create the brief prompt
    brief_prompt = f"""
    You are a content strategy specialist. Based on the following research, create a detailed content brief 
    with a strong focus on identifying content gaps and opportunities:
    
    {research_output.content}
    
    Include a section clearly labeled "Gap Analysis" that identifies specific content opportunities 
    competitors are missing or underserving.
    """
    
    try:
        # Initialize DeepSeek client with their API
        deepseek_client = OpenAI(
            api_key=deepseek_api_key, 
            base_url="https://api.deepseek.com"
        )
        
        logger.info(f"Making API request to DeepSeek")
        
        # Create the chat completion request
        brief_response = deepseek_client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a content strategy specialist."},
                {"role": "user", "content": brief_prompt}
            ],
            temperature=0.4,
            stream=False
        )
        
        # Get the brief content
        brief_output = brief_response.choices[0].message.content
        logger.info(f"Brief output received ({len(brief_output)} chars)")
        
    except Exception as e:
        logger.error(f"Error with DeepSeek API: {str(e)}")
        return None
    
    # Extract gap analysis for facts collection
    gap_analysis = None
    gap_section_pattern = r"(?i)(?:^|\n)#+\s*Gap Analysis\s*(?:\n|$)(.*?)(?=(?:^|\n)#+\s*|\Z)"
    import re
    match = re.search(gap_section_pattern, brief_output, re.DOTALL | re.MULTILINE)
    
    if match:
        gap_analysis = match.group(1).strip()
        logger.info(f"Gap Analysis extracted ({len(gap_analysis)} chars)")
    else:
        # Try more lenient extraction
        gap_pattern = r"(?i)Gap Analysis:?\s*(.*?)(?:\n\n|\n#|\Z)"
        match = re.search(gap_pattern, brief_output, re.DOTALL)
        if match:
            gap_analysis = match.group(1).strip()
            logger.info(f"Gap Analysis extracted with fallback method ({len(gap_analysis)} chars)")
        else:
            logger.warning("No Gap Analysis section found. Using generic extraction.")
            # Try to find any mentions of gaps or opportunities
            sentences = re.findall(r'[^.!?]*(?:gap|opportunity|missing|underserved)[^.!?]*[.!?]', brief_output, re.IGNORECASE)
            if sentences:
                gap_analysis = " ".join(sentences)
                logger.info(f"Generic gap analysis extracted ({len(gap_analysis)} chars)")
            else:
                gap_analysis = "No specific gap analysis found. Focus on gathering current facts and trends."
                logger.warning("Using default gap analysis")
    
    # Step 3: Facts collection with Grok using direct API
    logger.info("Step 3: Running Facts Collector (Grok/xAI) via direct API")
    
    # Get the xAI API key
    xai_api_key = os.getenv("XAI_API_KEY")
    if not xai_api_key:
        logger.error("XAI_API_KEY not found in environment variables")
        return None
    
    # Create a structured prompt for Grok
    facts_prompt = create_facts_prompt(topic, gap_analysis)
    logger.info(f"Created structured facts prompt with dynamic date and gap analysis")
    
    try:
        # Initialize client with xAI's API
        xai_client = OpenAI(
            api_key=xai_api_key, 
            base_url="https://api.x.ai/v1"
        )
        
        logger.info(f"Making API request to Grok")
        
        # Create the chat completion request
        facts_response = xai_client.chat.completions.create(
            model="grok-beta",
            messages=[
                {"role": "system", "content": "You are a helpful assistant with real-time internet access."},
                {"role": "user", "content": facts_prompt}
            ],
            temperature=0.7,
            stream=False
        )
        
        # Get the facts content
        facts_output = facts_response.choices[0].message.content
        logger.info(f"Facts output received ({len(facts_output)} chars)")
        
    except Exception as e:
        logger.error(f"Error with Grok API: {str(e)}")
        return None
    
    # Step 4: Content creation with Claude using direct API
    logger.info("Step 4: Running Content Creator (Claude) via direct API")
    
    # Get the Anthropic API key
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    if not anthropic_api_key:
        logger.error("ANTHROPIC_API_KEY not found in environment variables")
        return None
    
    # Create prompt for Claude
    content_prompt = f"""
    Create a 500-word {topic} article based on:
    
    RESEARCH:
    {research_output.content[:2000]}...
    
    CONTENT BRIEF:
    {brief_output[:2000]}...
    
    FACTS AND STATISTICS:
    {facts_output[:2000]}...
    
    The content should be helpful, practical, and engaging.
    """
    
    try:
        # Initialize Anthropic client
        claude_client = anthropic.Anthropic(api_key=anthropic_api_key)
        
        logger.info(f"Making API request to Claude")
        
        # Create the message
        content_response = claude_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=2000,
            temperature=0.7,
            system="You are a senior content creator for a leading publication.",
            messages=[
                {"role": "user", "content": content_prompt}
            ]
        )
        
        # Get the content
        content_output = content_response.content[0].text
        logger.info(f"Content output received ({len(content_output)} chars)")
        
    except Exception as e:
        logger.error(f"Error with Claude API: {str(e)}")
        return None
    
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
                "output": brief_output,
                "extracted_gap_analysis": gap_analysis
            },
            "facts": {
                "prompt": facts_prompt,
                "output": facts_output
            },
            "content": {
                "prompt": content_prompt,
                "output": content_output
            }
        }
    }
    
    # Save results to a file
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"integration_test_results_{timestamp}.json"
    
    with open(filename, "w") as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Integration test results saved to {filename}")
    
    return results

if __name__ == "__main__":
    if not check_api_keys():
        logger.error("Missing API keys. Please set all required API keys in .env file.")
        exit(1)
    
    # Run test with a suitable topic
    results = run_integration_test_direct("sustainable travel trends 2025")
    
    if results:
        logger.info("Integration test completed successfully!")
    else:
        logger.error("Integration test failed.") 