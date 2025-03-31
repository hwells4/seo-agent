"""
Test file demonstrating a complete content creation pipeline using OpenRouter 
with Agno for all agent steps.
"""

import os
import logging
import json
from dotenv import load_dotenv
from datetime import datetime
from agno.agent import Agent, Team
from agno.models.openrouter import OpenRouter
from agno.tools.duckduckgo import DuckDuckGoTools

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def create_content_creation_team():
    """
    Create a complete content creation team using Agno with OpenRouter models
    """
    # Check if the OpenRouter API key is set
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    if not openrouter_api_key:
        logger.error("OPENROUTER_API_KEY not found in environment variables")
        raise ValueError("OPENROUTER_API_KEY not found. Please set it in your environment or .env file")
    
    # 1. Research Agent using o3-mini
    research_agent = Agent(
        name="Research Engine",
        model=OpenRouter(
            id="openai/o3-mini",  # Using o3-mini for research
            max_tokens=1000,
            temperature=0.7,
            extra_request_options={
                "extra_body": {
                    "reasoning_effort": "high"  # High reasoning for complex analysis
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
    
    # 2. Brief Creation Agent using DeepSeek via OpenRouter
    brief_agent = Agent(
        name="Brief Creator",
        model=OpenRouter(
            id="deepseek/deepseek-chat",  # Using DeepSeek via OpenRouter
            max_tokens=800,
            temperature=0.6
        ),
        markdown=True,
        instructions="""
        You are a content strategy specialist.
        
        When given a research analysis:
        1. Identify content gaps and opportunities
        2. Create a detailed content brief that includes:
           - Recommended structure and outline
           - Key topics to cover thoroughly
           - Content differentiation strategy
           - E-E-A-T signals to include
           - Target word count and depth
        
        Your brief should provide clear direction for content creation
        that will outperform existing content.
        
        IMPORTANT: Include a section clearly labeled "Gap Analysis" that summarizes 
        the key content gaps and opportunities you've identified.
        """
    )
    
    # 3. Content Creation Agent using Claude via OpenRouter
    content_agent = Agent(
        name="Content Creator",
        model=OpenRouter(
            id="anthropic/claude-3-sonnet",  # Using Claude via OpenRouter
            max_tokens=1500,
            temperature=0.75
        ),
        markdown=True,
        instructions="""
        You are an expert content creator.
        
        When given a content brief and supporting facts:
        1. Create engaging, high-quality content that:
           - Follows the structure in the brief
           - Addresses all required topics thoroughly
           - Incorporates facts and figures naturally
           - Maintains a consistent, appropriate tone
           - Sounds authentically human, not AI-generated
           - Demonstrates expertise and authority
        
        Your content should be publication-ready and exceed
        the quality of competing content on the same topic.
        """
    )
    
    # Create the team with OpenRouter model for coordination
    content_team = Team(
        name="Content Creation Team",
        model=OpenRouter(
            id="openai/gpt-4o",  # Using GPT-4o via OpenRouter for coordination
            max_tokens=500,
            temperature=0.7
        ),
        members=[research_agent, brief_agent, content_agent],
        instructions="""
        You are the coordinator of a content creation team.
        Your job is to manage the entire content creation workflow:
        
        1. First, have the Research Engine analyze top content for the topic
        2. Next, have the Brief Creator develop a strategy based on the research
        3. Finally, have the Content Creator produce the final content
        
        Each step must build on the previous one's output.
        Ensure the final content follows the brief and incorporates all necessary research.
        """,
        markdown=True
    )
    
    return content_team

def test_content_creation_pipeline():
    """
    Test the complete content creation pipeline using OpenRouter with Agno
    """
    logger.info("Initializing content creation team with OpenRouter models")
    
    content_team = create_content_creation_team()
    
    # Test topic
    topic = "remote work productivity tools"
    
    try:
        logger.info(f"Starting content creation pipeline for topic: {topic}")
        
        # Define a short prompt for testing purposes
        prompt = f"""
        Create a 500-word article about '{topic}'.
        
        Follow these steps:
        1. Research the topic thoroughly
        2. Create a detailed content brief with structure
        3. Write the final article
        
        Make sure the content is engaging, informative, and optimized for search engines.
        """
        
        # Run the content creation team
        response = content_team.run(prompt)
        
        # Save the results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs("test_storage", exist_ok=True)
        
        # Save the final content
        with open(f"test_storage/final_content_{timestamp}.md", "w") as f:
            f.write(response.text)
        
        # Also save metadata
        metadata = {
            "topic": topic,
            "timestamp": timestamp,
            "models": {
                "coordinator": "openai/gpt-4o via OpenRouter",
                "research": "openai/o3-mini via OpenRouter",
                "brief": "deepseek/deepseek-chat via OpenRouter",
                "content": "anthropic/claude-3-sonnet via OpenRouter"
            },
            "response_length": len(response.text)
        }
        
        with open(f"test_storage/content_metadata_{timestamp}.json", "w") as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Content saved to test_storage/final_content_{timestamp}.md")
        logger.info(f"Metadata saved to test_storage/content_metadata_{timestamp}.json")
        logger.info("Test completed successfully!")
        
        return response.text
    
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    test_content_creation_pipeline() 