import os
import logging
import json
from dotenv import load_dotenv
from openai import OpenAI
import sys

# Add the parent directory to the path so we can import the TokenTracker
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from agents.utils.token_tracker import TokenTracker

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class OpenRouterTokenTracker:
    """
    A wrapper class to track token usage with OpenRouter using the TokenTracker.
    This handles the conversion from OpenRouter model names to our internal tracking names.
    """
    def __init__(self):
        # Define custom pricing for OpenRouter models
        custom_prices = {
            "openai": {
                "o3-mini": (0.0011, 0.0044),  # $1.10/M input, $4.40/M output
            }
        }
        
        self.token_tracker = TokenTracker(custom_prices=custom_prices)
        
    def track_usage(self, response, model_name="openai/o3-mini"):
        """Track token usage from an OpenRouter response"""
        # Extract the provider from the model name (e.g., "openai" from "openai/o3-mini")
        provider = model_name.split('/')[0] if '/' in model_name else "openai"
        model = model_name.split('/')[-1] if '/' in model_name else model_name
        
        # Extract token counts from the response
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        
        # Track usage based on the provider
        if provider == "openai":
            usage_data = self.token_tracker.track_openai(
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens
            )
        elif provider == "anthropic":
            usage_data = self.token_tracker.track_anthropic(
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens
            )
        else:
            # Use generic tracking for other providers
            usage_data = self.token_tracker.track_generic(
                provider=provider,
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                input_price=0.0011,  # Default price per 1K input tokens
                output_price=0.0044  # Default price per 1K output tokens
            )
            
        return usage_data
        
    def get_usage_report(self):
        """Get the complete usage report"""
        return self.token_tracker.get_usage_report()
        
    def save_usage_report(self, filename):
        """Save the usage report to a file"""
        report = self.get_usage_report()
        os.makedirs("test_storage", exist_ok=True)
        with open(f"test_storage/{filename}", "w") as f:
            json.dump(report, f, indent=2)
        return report

def test_openrouter_with_tracking():
    """
    Test OpenRouter integration with token tracking.
    This advanced test demonstrates how to track token usage when using OpenRouter.
    """
    # Get OpenRouter API key from environment variable
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    
    if not openrouter_api_key:
        logger.error("OPENROUTER_API_KEY not found in environment variables")
        raise ValueError("OPENROUTER_API_KEY not found. Please set it in your environment or .env file")
        
    logger.info("Testing OpenRouter with token tracking")
    
    # Initialize the token tracker
    token_tracker = OpenRouterTokenTracker()
    
    # Initialize OpenAI client with OpenRouter configuration
    client = OpenAI(
        api_key=openrouter_api_key,
        base_url="https://openrouter.ai/api/v1",
        default_headers={
            "HTTP-Referer": "https://seo-agent.example.com/",  # Replace with your site URL
            "X-Title": "SEO Agent"  # Optional - your app name
        }
    )
    
    # Test prompts for SEO analysis
    prompts = [
        "What are the top 3 on-page SEO factors to focus on in 2024?",
        "Explain how content length affects SEO rankings in 100 words or less."
    ]
    
    results = []
    
    try:
        for i, prompt in enumerate(prompts):
            logger.info(f"Testing prompt {i+1}: {prompt}")
            
            # Create a completion using o3-mini
            response = client.chat.completions.create(
                model="openai/o3-mini",  # Use o3-mini model through OpenRouter
                messages=[
                    {"role": "system", "content": "You are a helpful SEO research assistant with expertise in content optimization."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200,
                extra_body={
                    "reasoning_effort": "high"  # Can be "low", "medium", or "high"
                }
            )
            
            # Extract and display the response
            result = response.choices[0].message.content
            logger.info(f"Response {i+1}: {result}")
            
            # Track token usage for this response
            usage_data = token_tracker.track_usage(response, "openai/o3-mini")
            logger.info(f"Tokens for prompt {i+1}: {usage_data['input_tokens']} input, {usage_data['output_tokens']} output")
            logger.info(f"Cost for prompt {i+1}: ${usage_data['total_cost']:.6f}")
            
            # Add to results
            results.append({
                "prompt": prompt,
                "response": result,
                "usage": {
                    "input_tokens": usage_data['input_tokens'],
                    "output_tokens": usage_data['output_tokens'],
                    "total_cost": usage_data['total_cost']
                }
            })
        
        # Save comprehensive results
        os.makedirs("test_storage", exist_ok=True)
        with open("test_storage/openrouter_advanced_test_results.json", "w") as f:
            json.dump(results, f, indent=2)
            
        # Save token usage report
        usage_report = token_tracker.save_usage_report("openrouter_token_usage.json")
        
        logger.info(f"Complete test results saved to test_storage/openrouter_advanced_test_results.json")
        logger.info(f"Token usage report saved to test_storage/openrouter_token_usage.json")
        
        # Summary of total usage
        total_usage = usage_report["total"]
        logger.info(f"Total tokens used: {total_usage['input_tokens'] + total_usage['output_tokens']}")
        logger.info(f"Total cost: ${total_usage['cost']:.6f}")
        
        return results
        
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        raise
        
if __name__ == "__main__":
    test_openrouter_with_tracking() 