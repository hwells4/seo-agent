#!/usr/bin/env python3
"""
Test script to check if DuckDuckGo search is working properly
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("duckduckgo_test")

# Add the parent directory to the path to import agents modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import token tracker to measure usage
from agents.utils.token_tracker import token_tracker

# Import Agno components
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools

# Load environment variables
load_dotenv()

# Ensure test_storage directory exists
os.makedirs("test_storage", exist_ok=True)

def test_duckduckgo_search():
    """Test DuckDuckGo search functionality"""
    # Reset token tracker
    token_tracker.reset()
    
    # Get API key
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        logger.error("OPENAI_API_KEY environment variable is not set")
        return False
    
    try:
        # Create a test agent with DuckDuckGo tools
        agent = Agent(
            name="DuckDuckGoTester",
            model=OpenAIChat(id="gpt-3.5-turbo", api_key=openai_api_key),
            tools=[DuckDuckGoTools()],
            instructions="""
            You are a helpful assistant. When asked a question, use the DuckDuckGo search tool to find and
            provide current information about the topic.
            
            Provide a brief summary of the search results for the query.
            """
        )
        
        # Run a simple search
        prompt = "Search for 'latest developments in SEO' and provide a brief summary of the results"
        logger.info(f"Running DuckDuckGo search with prompt: '{prompt}'")
        
        response = agent.run(prompt)
        content = response.content if hasattr(response, 'content') else str(response)
        
        # Track token usage
        token_tracker.track_step(
            step_name="duckduckgo_test",
            provider="openai",
            model="gpt-3.5-turbo",
            input_text=prompt,
            output_text=content
        )
        
        # Output the response
        logger.info(f"DuckDuckGo search response ({len(content)} chars)")
        print("\n===== DUCKDUCKGO SEARCH RESULTS =====")
        print(content)
        print("=====================================\n")
        
        # Print token usage
        token_tracker.print_usage_report()
        
        # Save response content
        with open("test_storage/duckduckgo_test_results.txt", "w") as f:
            f.write(content)
        logger.info("Results saved to test_storage/duckduckgo_test_results.txt")
        
        # Save a token usage report
        token_tracker.save_report_to_file("test_storage/duckduckgo_test_usage.json")
        logger.info("Token usage saved to test_storage/duckduckgo_test_usage.json")
        
        return "search" in content.lower() and len(content) > 100
    
    except Exception as e:
        logger.error(f"Error testing DuckDuckGo search: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def main():
    """Main function to run the DuckDuckGo test"""
    success = test_duckduckgo_search()
    
    if success:
        logger.info("DuckDuckGo search test completed successfully")
        return 0
    else:
        logger.error("DuckDuckGo search test failed")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 