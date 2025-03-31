#!/usr/bin/env python3
"""
Mini test for Content Creation Team with shortened responses
This is designed to test the system with minimal token usage by:
1. Using system mocking for non-critical components
2. Limiting max tokens for all responses
3. Using shorter test prompts
"""

import os
import logging
import json
import datetime
import re
from dotenv import load_dotenv

from content_creation_team import create_content_team, extract_gap_analysis

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

def test_content_creation_mini():
    """Run a minimal test of the content creation team with short outputs
    
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
        
        logger.info("Running mini test of content creation team")
        
        # Simplified brand voice to reduce tokens
        brand_voice = {
            "tone": "Conversational but professional",
            "style": "Direct and practical",
            "taboo_words": ["obviously", "simply", "just", "clearly"]
        }
        
        # Create the team
        team = create_content_team(brand_voice)
        
        # Override model max tokens to limit response sizes (optional)
        for member in team.members:
            # If the model has a max_tokens parameter, set it low
            if hasattr(member.model, 'max_tokens'):
                member.model.max_tokens = 300
        
        # Simple topic that won't require extensive research
        topic = "desk organization mini test"
        
        logger.info(f"Starting mini test with topic: {topic}")
        
        # Use a shorter, more focused request
        result = team.print_response(
            message=f"Create a 150-word outline about {topic}. Keep all responses concise.",
            stream=True,
            stream_intermediate_steps=True
        )
        
        # Save the mini test results to a file
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"mini_test_results_{timestamp}.json"
        
        with open(filename, "w") as f:
            result_data = {
                "topic": topic,
                "content": result if isinstance(result, str) else str(result),
                "timestamp": timestamp,
                "test_type": "mini"
            }
            json.dump(result_data, f, indent=2)
        
        logger.info(f"Mini test results saved to {filename}")
        return result
    
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
    print("Running mini tests for content creation team")
    print("--------------------------------------------")
    
    # Test gap analysis extraction
    test_gap_analysis_extraction()
    
    # Run mini content creation test
    result = test_content_creation_mini()
    
    if result:
        print("\nMini test completed successfully!")
    else:
        print("\nMini test failed.") 