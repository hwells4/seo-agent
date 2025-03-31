import os
import time
import json
from dotenv import load_dotenv
import logging
from typing import Dict, Any, Optional

# Load the token tracker
from token_tracker import token_tracker

# Import Agno components
from agno.agent import Agent, RunResponse
from agno.models.openai import OpenAIChat
from agno.models.anthropic import Claude
from agno.models.deepseek import DeepSeek
from agno.models.xai import xAI

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("token_tracker_example")

# Load environment variables
load_dotenv()

def check_api_keys():
    """Check if all required API keys are set."""
    required_keys = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
        "DEEPSEEK_API_KEY": os.getenv("DEEPSEEK_API_KEY"),
        "XAI_API_KEY": os.getenv("XAI_API_KEY"),
    }
    
    missing_keys = [key for key, value in required_keys.items() if not value]
    
    if missing_keys:
        logger.warning(f"Missing API keys: {', '.join(missing_keys)}")
    
    return not missing_keys

def estimate_tokens(text: str) -> int:
    """
    Estimate the number of tokens in a string.
    This is a very rough estimate - about 4 characters per token.
    """
    return len(text) // 4

def track_response_tokens(provider: str, model: str, prompt: str, response: str, 
                         response_metadata: Optional[Dict] = None):
    """
    Track token usage for a response.
    This is an estimation since Agno doesn't directly expose token counts.
    """
    # Estimate input and output tokens
    input_tokens = estimate_tokens(prompt)
    output_tokens = estimate_tokens(response)
    
    # Track based on provider
    if provider == "openai":
        token_tracker.track_openai(model, input_tokens, output_tokens, response_metadata)
    elif provider == "anthropic":
        token_tracker.track_anthropic(model, input_tokens, output_tokens, response_metadata)
    elif provider == "deepseek":
        token_tracker.track_deepseek(model, input_tokens, output_tokens, response_metadata)
    elif provider == "xai":
        token_tracker.track_xai(model, input_tokens, output_tokens, response_metadata)
    else:
        # Default to generic tracking with estimated pricing
        token_tracker.track_generic(
            provider, model, input_tokens, output_tokens, 
            input_price=0.001, output_price=0.002, response_metadata=response_metadata
        )
    
    logger.info(f"Tracked usage for {provider} ({model}): {input_tokens} input, {output_tokens} output tokens")

def run_openai_test():
    """Run a test with OpenAI's model and track usage."""
    logger.info("Testing OpenAI GPT-3.5 Turbo model...")
    
    prompt = "Write a short paragraph about sustainable travel in 2025."
    
    agent = Agent(
        model=OpenAIChat(id="gpt-3.5-turbo"),
        markdown=True
    )
    
    response = agent.run(prompt)
    
    # Track tokens
    track_response_tokens("openai", "gpt-3.5-turbo", prompt, response)
    
    return response

def run_anthropic_test():
    """Run a test with Anthropic's Claude model and track usage."""
    logger.info("Testing Anthropic Claude 3 Sonnet model...")
    
    prompt = "What are the key considerations for creating eco-friendly travel content?"
    
    agent = Agent(
        model=Claude(id="claude-3-sonnet"),
        markdown=True
    )
    
    response = agent.run(prompt)
    
    # Track tokens
    track_response_tokens("anthropic", "claude-3-sonnet", prompt, response)
    
    return response

def run_deepseek_test():
    """Run a test with DeepSeek's model and track usage."""
    logger.info("Testing DeepSeek Chat model...")
    
    prompt = "Create a brief content outline for an article about regenerative tourism."
    
    # Use API key explicitly
    api_key = os.getenv("DEEPSEEK_API_KEY")
    agent = Agent(
        model=DeepSeek(api_key=api_key),
        markdown=True
    )
    
    response = agent.run(prompt)
    
    # Track tokens
    track_response_tokens("deepseek", "deepseek-chat", prompt, response)
    
    return response

def run_xai_test():
    """Run a test with xAI's model and track usage."""
    logger.info("Testing xAI Grok model...")
    
    prompt = "What are the latest trends in AI-powered travel planning tools?"
    
    # Use API key explicitly
    api_key = os.getenv("XAI_API_KEY")
    agent = Agent(
        model=xAI(api_key=api_key),
        markdown=True
    )
    
    response = agent.run(prompt)
    
    # Track tokens
    track_response_tokens("xai", "grok-1", prompt, response)
    
    return response

def run_all_tests():
    """Run tests for all supported models and track token usage."""
    try:
        # Reset the token tracker
        token_tracker.reset()
        
        # Run tests for each model
        responses = {}
        
        # Test OpenAI
        if os.getenv("OPENAI_API_KEY"):
            responses["openai"] = run_openai_test()
            time.sleep(1)  # Brief pause between API calls
        else:
            logger.warning("Skipping OpenAI test - API key not found")
        
        # Test Anthropic
        if os.getenv("ANTHROPIC_API_KEY"):
            responses["anthropic"] = run_anthropic_test()
            time.sleep(1)
        else:
            logger.warning("Skipping Anthropic test - API key not found")
        
        # Test DeepSeek
        if os.getenv("DEEPSEEK_API_KEY"):
            responses["deepseek"] = run_deepseek_test()
            time.sleep(1)
        else:
            logger.warning("Skipping DeepSeek test - API key not found")
        
        # Test xAI
        if os.getenv("XAI_API_KEY"):
            responses["xai"] = run_xai_test()
        else:
            logger.warning("Skipping xAI test - API key not found")
        
        # Print token usage report
        token_tracker.print_usage_report()
        
        # Save results
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        
        # Save token usage report
        token_tracker.save_report_to_file(f"token_usage_{timestamp}.json")
        
        # Save model responses
        with open(f"model_responses_{timestamp}.json", "w") as f:
            json.dump(responses, f, indent=2)
        
        logger.info(f"Test results saved to model_responses_{timestamp}.json")
        logger.info(f"Token usage report saved to token_usage_{timestamp}.json")
        
    except Exception as e:
        logger.error(f"Error running tests: {e}")

if __name__ == "__main__":
    logger.info("Starting token tracking example...")
    
    if check_api_keys():
        logger.info("All API keys are set")
        run_all_tests()
    else:
        logger.warning("Some API keys are missing. Tests will be skipped for those models.")
        run_all_tests() 