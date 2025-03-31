#!/usr/bin/env python3
"""
Test script to verify Grok's real-time data capabilities with structured prompts using direct API access
"""

import os
import logging
import datetime
import json
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("grok_test")

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

def test_grok_direct_api():
    """Test Grok's real-time capabilities using direct API access"""
    
    # Check for API key
    xai_api_key = os.getenv("XAI_API_KEY")
    if not xai_api_key:
        logger.error("XAI_API_KEY not found in environment variables")
        return {"success": False, "error": "XAI_API_KEY not found"}
    
    # Test topic
    topic = "sustainable travel trends 2025"
    
    # Sample gap analysis
    gap_analysis = "Competitor analysis shows most blogs on 'sustainable travel trends 2025' focus heavily on airline carbon offsets (80% of top 10 SERP results), but searches for 'eco-friendly accommodations 2025' are up 20% this month per Google Trends, with little coverage. Social media posts also mention confusion around offset credibility, an angle only 2/10 competitors address."
    
    # Create the structured prompt
    prompt = create_facts_prompt(topic, gap_analysis)
    
    try:
        # Initialize client with xAI's API
        client = OpenAI(
            api_key=xai_api_key, 
            base_url="https://api.x.ai/v1"
        )
        
        logger.info(f"Making API request to Grok with topic: {topic}")
        
        # Create the chat completion request
        response = client.chat.completions.create(
            model="grok-beta",
            messages=[
                {"role": "system", "content": "You are a helpful assistant with real-time internet access."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            stream=False
        )
        
        # Get the response content
        response_content = response.choices[0].message.content
        
        # Try to parse as JSON
        try:
            # If response is in a code block, extract it
            if '```json' in response_content:
                json_part = response_content.split('```json')[1].split('```')[0]
                parsed_json = json.loads(json_part.strip())
            else:
                # Try parsing the whole response as JSON
                parsed_json = json.loads(response_content)
            
            # Save results
            results = {
                "success": True,
                "topic": topic,
                "prompt": prompt,
                "response": response_content,
                "parsed_json": parsed_json
            }
            
        except json.JSONDecodeError:
            # If not valid JSON, just return the raw response
            results = {
                "success": True,
                "topic": topic,
                "prompt": prompt,
                "response": response_content,
                "error": "Could not parse as JSON"
            }
        
        # Save the result to a file
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"grok_realtime_test_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Test results saved to {filename}")
        
        return results
    
    except Exception as e:
        logger.error(f"Error running direct Grok API test: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "topic": topic,
            "prompt": prompt
        }

if __name__ == "__main__":
    logger.info("Starting direct Grok real-time data test")
    results = test_grok_direct_api()
    
    if results["success"]:
        logger.info("Test completed successfully")
        # Print a snippet of the response
        logger.info(f"Response snippet: {results['response'][:150]}...")
    else:
        logger.error(f"Test failed: {results.get('error', 'Unknown error')}") 