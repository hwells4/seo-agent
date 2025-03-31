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

def test_openrouter_o3_mini():
    """
    Test integration with OpenRouter using o3-mini model.
    This test creates a simple chat completion to verify connectivity and functionality.
    """
    # Get OpenRouter API key from environment variable
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    
    if not openrouter_api_key:
        logger.error("OPENROUTER_API_KEY not found in environment variables")
        raise ValueError("OPENROUTER_API_KEY not found. Please set it in your environment or .env file")
        
    logger.info("Testing OpenRouter with o3-mini model")
    
    # Initialize OpenAI client with OpenRouter configuration
    client = OpenAI(
        api_key=openrouter_api_key,
        base_url="https://openrouter.ai/api/v1",
        default_headers={
            "HTTP-Referer": "https://seo-agent.example.com/",  # Replace with your site URL
            "X-Title": "SEO Agent"  # Optional - your app name
        }
    )
    
    # Define a test prompt
    prompt = "Analyze the SEO potential of the keyword 'content marketing strategies' in 2-3 sentences"
    
    try:
        # Create a completion using o3-mini
        response = client.chat.completions.create(
            model="openai/o3-mini",  # Use o3-mini model through OpenRouter
            messages=[
                {"role": "system", "content": "You are a helpful SEO research assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=150,
            # Optional: Set reasoning effort for o3-mini
            extra_body={
                "reasoning_effort": "high"  # Can be "low", "medium", or "high"
            }
        )
        
        # Extract and display the response
        result = response.choices[0].message.content
        logger.info(f"OpenRouter o3-mini response: {result}")
        
        # Save response to a file for analysis
        os.makedirs("test_storage", exist_ok=True)
        with open("test_storage/openrouter_o3mini_test.json", "w") as f:
            # Convert response object to dictionary and save
            response_dict = {
                "model": response.model,
                "content": result,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
            json.dump(response_dict, f, indent=2)
            
        logger.info(f"Response saved to test_storage/openrouter_o3mini_test.json")
        
        # Verify the response is non-empty
        assert result, "Response is empty"
        
        # Log usage information
        logger.info(f"Tokens used: {response.usage.total_tokens} (Prompt: {response.usage.prompt_tokens}, Completion: {response.usage.completion_tokens})")
        
        return True
        
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        raise
        
if __name__ == "__main__":
    test_openrouter_o3_mini() 