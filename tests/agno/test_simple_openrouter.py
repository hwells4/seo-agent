"""
Test file demonstrating direct OpenRouter API usage with the OpenAI SDK.
This bypasses Agno completely to test if the OpenRouter API key is working correctly.
"""

import os
import logging
import json
from dotenv import load_dotenv
from openai import OpenAI

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def test_simple_openrouter():
    """
    Test direct integration with OpenRouter using the OpenAI SDK.
    This is a simple test to verify that the OpenRouter API key is working.
    """
    # Get OpenRouter API key from environment variable
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    
    if not openrouter_api_key:
        logger.error("OPENROUTER_API_KEY not found in environment variables")
        raise ValueError("OPENROUTER_API_KEY not found. Please set it in your environment or .env file")
    else:
        # Log a masked version of the API key
        masked_key = openrouter_api_key[:4] + "..." + openrouter_api_key[-4:] if len(openrouter_api_key) > 8 else "***"
        logger.info(f"OPENROUTER_API_KEY found: {masked_key}")
        
    logger.info("Testing direct OpenRouter integration with OpenAI SDK")
    
    # Initialize OpenAI client with OpenRouter configuration
    client = OpenAI(
        api_key=openrouter_api_key,
        base_url="https://openrouter.ai/api/v1",
        default_headers={
            "HTTP-Referer": "https://seo-agent.example.com/",  # Your site URL
            "X-Title": "SEO Agent"  # Your app name
        }
    )
    
    # Define a test prompt
    prompt = "Explain the concept of SEO in one sentence."
    
    try:
        # Create a completion using o3-mini
        response = client.chat.completions.create(
            model="openai/o3-mini",  # Use o3-mini model
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=150
        )
        
        # Extract and display the response
        result = response.choices[0].message.content
        logger.info(f"OpenRouter response: {result}")
        
        # Show token usage
        if hasattr(response, 'usage'):
            logger.info(f"Tokens used: {response.usage.total_tokens} (Prompt: {response.usage.prompt_tokens}, Completion: {response.usage.completion_tokens})")
        
        # Save response to a file
        os.makedirs("test_storage", exist_ok=True)
        with open("test_storage/simple_openrouter_test.json", "w") as f:
            # Convert response object to dictionary
            response_dict = {
                "model": response.model,
                "content": result,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                } if hasattr(response, 'usage') else None
            }
            json.dump(response_dict, f, indent=2)
            
        logger.info(f"Response saved to test_storage/simple_openrouter_test.json")
        
        # Create a completion using a different model (gpt-4o) since o3-mini might have issues
        response = client.chat.completions.create(
            model="openai/gpt-4o",  # Use gpt-4o model as a fallback
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=150
        )
        
        # Create a completion using a different model (gpt-4o) since o3-mini might have issues
        logger.info("Trying with gpt-4o model as fallback")
        response2 = client.chat.completions.create(
            model="openai/gpt-4o",  # Use gpt-4o model as a fallback
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=150
        )
        
        # Extract and display the response
        result2 = response2.choices[0].message.content
        logger.info(f"OpenRouter gpt-4o response: {result2}")
        
        # Show token usage
        if hasattr(response2, 'usage'):
            logger.info(f"gpt-4o tokens used: {response2.usage.total_tokens} (Prompt: {response2.usage.prompt_tokens}, Completion: {response2.usage.completion_tokens})")
        
        # Save response to a file
        with open("test_storage/simple_openrouter_gpt4o_test.json", "w") as f:
            response_dict2 = {
                "model": response2.model,
                "content": result2,
                "usage": {
                    "prompt_tokens": response2.usage.prompt_tokens,
                    "completion_tokens": response2.usage.completion_tokens,
                    "total_tokens": response2.usage.total_tokens
                } if hasattr(response2, 'usage') else None
            }
            json.dump(response_dict2, f, indent=2)
            
        logger.info(f"gpt-4o response saved to test_storage/simple_openrouter_gpt4o_test.json")
        
        return True
        
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        raise
        
if __name__ == "__main__":
    test_simple_openrouter() 