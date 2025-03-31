"""
Test file demonstrating the use of OpenRouter with Agno to access o3-mini model.
"""

import os
import logging
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.openrouter import OpenRouter

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def test_agno_openrouter():
    """
    Test using Agno with OpenRouter to access o3-mini model with non-streaming approach
    """
    # Check if the OpenRouter API key is set
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    if not openrouter_api_key:
        logger.error("OPENROUTER_API_KEY not found in environment variables")
        raise ValueError("OPENROUTER_API_KEY not found. Please set it in your environment or .env file")
    else:
        # Log a masked version of the API key to verify it's loaded
        masked_key = openrouter_api_key[:4] + "..." + openrouter_api_key[-4:] if len(openrouter_api_key) > 8 else "***"
        logger.info(f"OPENROUTER_API_KEY found: {masked_key}")
    
    logger.info("Testing Agno with OpenRouter o3-mini")
    
    try:
        # Create an agent using OpenRouter with o3-mini model
        agent = Agent(
            model=OpenRouter(
                id="openai/o3-mini",  # Specify the o3-mini model
                max_tokens=150,
                temperature=0.7,
                api_key=openrouter_api_key  # Explicitly pass the API key
            ),
            markdown=True,
            instructions="You are a helpful SEO research assistant that provides concise analyses."
        )
        
        # Test with a simple SEO-related query
        prompt = "Analyze the SEO potential of the keyword 'content marketing strategies' in 2-3 sentences"
        
        # Use run with stream=False to get a non-streaming response
        logger.info("Sending prompt to o3-mini via OpenRouter (non-streaming)...")
        response = agent.run(prompt, stream=False)
        
        # Log the response for debugging
        logger.info(f"Response type: {type(response)}")
        logger.info(f"Response: {response}")
        
        # Attempt to get response text based on common formats
        response_text = ""
        
        # Try different ways to extract the text from the response
        if hasattr(response, 'content'):
            response_text = response.content
        elif hasattr(response, 'text'):
            response_text = response.text
        elif isinstance(response, str):
            response_text = response
        else:
            response_text = str(response)
        
        logger.info(f"Received response: {response_text}")
        
        # Save the response to a file
        os.makedirs("test_storage", exist_ok=True)
        with open("test_storage/agno_openrouter_test.txt", "w") as f:
            f.write(response_text)
        
        logger.info(f"Response saved to test_storage/agno_openrouter_test.txt")
        logger.info("Test completed successfully!")
        
        return True
    
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        
        # Fall back to print_response approach if run fails
        try:
            logger.info("Falling back to print_response method...")
            response = agent.print_response(prompt, stream=False)
            
            logger.info("Response printed to console")
            logger.info("Test completed with partial success (printed but not captured programmatically)")
            return True
            
        except Exception as nested_e:
            logger.error(f"Fallback also failed: {str(nested_e)}")
            raise e

if __name__ == "__main__":
    test_agno_openrouter() 