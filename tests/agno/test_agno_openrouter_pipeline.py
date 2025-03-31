"""
Test file demonstrating the integration of OpenRouter with Agno 
for a Research Agent in the content pipeline.
"""

import os
import logging
import json
from dotenv import load_dotenv
from datetime import datetime
from agno.agent import Agent
from agno.models.openrouter import OpenRouter
from agno.tools.duckduckgo import DuckDuckGoTools

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def create_research_agent():
    """
    Create a research agent using Agno with OpenRouter's o3-mini model
    """
    # Check if the OpenRouter API key is set
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    if not openrouter_api_key:
        logger.error("OPENROUTER_API_KEY not found in environment variables")
        raise ValueError("OPENROUTER_API_KEY not found. Please set it in your environment or .env file")
    
    # Create an agent using OpenRouter with o3-mini model
    research_agent = Agent(
        name="Research Engine",
        model=OpenRouter(
            id="openai/o3-mini",  # Specify the o3-mini model
            max_tokens=1000,
            temperature=0.7,
            # Add o3-mini specific parameters
            extra_request_options={
                "extra_body": {
                    "reasoning_effort": "high"  # Use high reasoning effort for research tasks
                }
            }
        ),
        markdown=True,
        tools=[DuckDuckGoTools()],
        instructions="""
        You are a content research specialist.
        
        When given a topic:
        1. Search for top-ranking content on this topic
        2. Analyze their structure, style, and coverage
        3. Identify common topics, subtopics, and patterns
        4. Determine content styles that perform well
        5. Provide a comprehensive analysis summary
        
        Your output should be a detailed analysis report that includes:
        - Key topics covered by top-performing content
        - Common content structures and formats
        - Typical tone and style elements
        - Depth of coverage in successful content
        - Notable authority signals used
        """
    )
    
    return research_agent

def test_research_pipeline():
    """
    Test the research agent in a content pipeline
    """
    logger.info("Initializing research agent with OpenRouter o3-mini")
    
    research_agent = create_research_agent()
    
    # Test topic
    topic = "content marketing strategies for SaaS companies"
    
    try:
        logger.info(f"Starting research on topic: {topic}")
        
        # Run the research agent
        response = research_agent.run(f"Research and analyze content about '{topic}'. Use search tools as needed to gather data from top-ranking content.")
        
        # Save the research results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs("test_storage", exist_ok=True)
        
        # Save the text response
        with open(f"test_storage/research_result_{timestamp}.txt", "w") as f:
            f.write(response.text)
        
        # Also save metadata as JSON
        metadata = {
            "topic": topic,
            "timestamp": timestamp,
            "model": "openai/o3-mini via OpenRouter",
            "response_length": len(response.text)
        }
        
        with open(f"test_storage/research_metadata_{timestamp}.json", "w") as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Research results saved to test_storage/research_result_{timestamp}.txt")
        logger.info(f"Research metadata saved to test_storage/research_metadata_{timestamp}.json")
        logger.info("Test completed successfully!")
        
        return response.text
    
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    test_research_pipeline() 