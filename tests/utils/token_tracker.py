import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Union, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("token_tracker")

class TokenTracker:
    """
    A utility class to track token usage and calculate costs across different LLM providers.
    """
    
    # Default token prices per 1000 tokens (input, output) as of March 2025
    DEFAULT_PRICES = {
        "openai": {
            "gpt-3.5-turbo": (0.0005, 0.0015),  # $0.0005 per 1K input, $0.0015 per 1K output
            "gpt-4o": (0.005, 0.015),           # $0.005 per 1K input, $0.015 per 1K output
            "gpt-4": (0.03, 0.06),              # $0.03 per 1K input, $0.06 per 1K output
        },
        "anthropic": {
            "claude-3-sonnet": (0.003, 0.015),  # $0.003 per 1K input, $0.015 per 1K output
            "claude-3-opus": (0.015, 0.075),    # $0.015 per 1K input, $0.075 per 1K output
            "claude-3-haiku": (0.00025, 0.00125) # $0.00025 per 1K input, $0.00125 per 1K output
        },
        "deepseek": {
            "deepseek-chat": (0.0005, 0.0015),  # Approximate - may need updating
        },
        "xai": {
            "grok-1": (0.0005, 0.0015),         # Approximate - may need updating
        }
    }
    
    def __init__(self, custom_prices: Optional[Dict] = None):
        """
        Initialize the token tracker with optional custom pricing.
        
        Args:
            custom_prices: Optional dictionary with custom pricing for models
        """
        self.usage = {
            "openai": {"input_tokens": 0, "output_tokens": 0, "cost": 0.0, "calls": 0},
            "anthropic": {"input_tokens": 0, "output_tokens": 0, "cost": 0.0, "calls": 0},
            "deepseek": {"input_tokens": 0, "output_tokens": 0, "cost": 0.0, "calls": 0},
            "xai": {"input_tokens": 0, "output_tokens": 0, "cost": 0.0, "calls": 0},
            "total": {"input_tokens": 0, "output_tokens": 0, "cost": 0.0, "calls": 0}
        }
        
        self.prices = self.DEFAULT_PRICES.copy()
        if custom_prices:
            self._update_prices(custom_prices)
        
        self.session_start = datetime.now()
        self.last_tracked = None
        
    def _update_prices(self, custom_prices: Dict):
        """Update the pricing dictionary with custom values."""
        for provider, models in custom_prices.items():
            if provider not in self.prices:
                self.prices[provider] = {}
            
            for model, price in models.items():
                self.prices[provider][model] = price
    
    def track_openai(self, 
                    model: str, 
                    input_tokens: int, 
                    output_tokens: int, 
                    response_metadata: Optional[Dict] = None) -> Dict:
        """
        Track token usage for OpenAI models.
        
        Args:
            model: The OpenAI model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            response_metadata: Optional response metadata from the API
            
        Returns:
            Dictionary with usage information
        """
        provider = "openai"
        
        # Get pricing
        model_key = model.split(':')[-1] if ':' in model else model
        model_prices = self.prices[provider].get(
            model_key, 
            self.prices[provider].get("gpt-3.5-turbo")  # Default fallback
        )
        
        # Calculate cost
        input_cost = (input_tokens / 1000) * model_prices[0]
        output_cost = (output_tokens / 1000) * model_prices[1]
        total_cost = input_cost + output_cost
        
        # Update usage
        self.usage[provider]["input_tokens"] += input_tokens
        self.usage[provider]["output_tokens"] += output_tokens
        self.usage[provider]["cost"] += total_cost
        self.usage[provider]["calls"] += 1
        
        # Update totals
        self.usage["total"]["input_tokens"] += input_tokens
        self.usage["total"]["output_tokens"] += output_tokens
        self.usage["total"]["cost"] += total_cost
        self.usage["total"]["calls"] += 1
        
        self.last_tracked = datetime.now()
        
        usage_data = {
            "provider": provider,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost": total_cost,
            "timestamp": self.last_tracked.isoformat()
        }
        
        logger.debug(f"Tracked {provider} usage: {input_tokens} input tokens, {output_tokens} output tokens, ${total_cost:.6f}")
        return usage_data
    
    def track_anthropic(self, 
                       model: str, 
                       input_tokens: int, 
                       output_tokens: int, 
                       response_metadata: Optional[Dict] = None) -> Dict:
        """
        Track token usage for Anthropic Claude models.
        
        Args:
            model: The Claude model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            response_metadata: Optional response metadata from the API
            
        Returns:
            Dictionary with usage information
        """
        provider = "anthropic"
        
        # Get pricing
        model_key = model.split(':')[-1] if ':' in model else model
        model_prices = self.prices[provider].get(
            model_key, 
            self.prices[provider].get("claude-3-sonnet")  # Default fallback
        )
        
        # Calculate cost
        input_cost = (input_tokens / 1000) * model_prices[0]
        output_cost = (output_tokens / 1000) * model_prices[1]
        total_cost = input_cost + output_cost
        
        # Update usage
        self.usage[provider]["input_tokens"] += input_tokens
        self.usage[provider]["output_tokens"] += output_tokens
        self.usage[provider]["cost"] += total_cost
        self.usage[provider]["calls"] += 1
        
        # Update totals
        self.usage["total"]["input_tokens"] += input_tokens
        self.usage["total"]["output_tokens"] += output_tokens
        self.usage["total"]["cost"] += total_cost
        self.usage["total"]["calls"] += 1
        
        self.last_tracked = datetime.now()
        
        usage_data = {
            "provider": provider,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost": total_cost,
            "timestamp": self.last_tracked.isoformat()
        }
        
        logger.debug(f"Tracked {provider} usage: {input_tokens} input tokens, {output_tokens} output tokens, ${total_cost:.6f}")
        return usage_data
    
    def track_deepseek(self, 
                      model: str, 
                      input_tokens: int, 
                      output_tokens: int, 
                      response_metadata: Optional[Dict] = None) -> Dict:
        """
        Track token usage for DeepSeek models.
        
        Args:
            model: The DeepSeek model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            response_metadata: Optional response metadata from the API
            
        Returns:
            Dictionary with usage information
        """
        provider = "deepseek"
        
        # Get pricing
        model_key = model.split(':')[-1] if ':' in model else model
        model_prices = self.prices[provider].get(
            model_key, 
            self.prices[provider].get("deepseek-chat")  # Default fallback
        )
        
        # Calculate cost
        input_cost = (input_tokens / 1000) * model_prices[0]
        output_cost = (output_tokens / 1000) * model_prices[1]
        total_cost = input_cost + output_cost
        
        # Update usage
        self.usage[provider]["input_tokens"] += input_tokens
        self.usage[provider]["output_tokens"] += output_tokens
        self.usage[provider]["cost"] += total_cost
        self.usage[provider]["calls"] += 1
        
        # Update totals
        self.usage["total"]["input_tokens"] += input_tokens
        self.usage["total"]["output_tokens"] += output_tokens
        self.usage["total"]["cost"] += total_cost
        self.usage["total"]["calls"] += 1
        
        self.last_tracked = datetime.now()
        
        usage_data = {
            "provider": provider,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost": total_cost,
            "timestamp": self.last_tracked.isoformat()
        }
        
        logger.debug(f"Tracked {provider} usage: {input_tokens} input tokens, {output_tokens} output tokens, ${total_cost:.6f}")
        return usage_data
    
    def track_xai(self, 
                 model: str, 
                 input_tokens: int, 
                 output_tokens: int, 
                 response_metadata: Optional[Dict] = None) -> Dict:
        """
        Track token usage for xAI models.
        
        Args:
            model: The xAI model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            response_metadata: Optional response metadata from the API
            
        Returns:
            Dictionary with usage information
        """
        provider = "xai"
        
        # Get pricing
        model_key = model.split(':')[-1] if ':' in model else model
        model_prices = self.prices[provider].get(
            model_key, 
            self.prices[provider].get("grok-1")  # Default fallback
        )
        
        # Calculate cost
        input_cost = (input_tokens / 1000) * model_prices[0]
        output_cost = (output_tokens / 1000) * model_prices[1]
        total_cost = input_cost + output_cost
        
        # Update usage
        self.usage[provider]["input_tokens"] += input_tokens
        self.usage[provider]["output_tokens"] += output_tokens
        self.usage[provider]["cost"] += total_cost
        self.usage[provider]["calls"] += 1
        
        # Update totals
        self.usage["total"]["input_tokens"] += input_tokens
        self.usage["total"]["output_tokens"] += output_tokens
        self.usage["total"]["cost"] += total_cost
        self.usage["total"]["calls"] += 1
        
        self.last_tracked = datetime.now()
        
        usage_data = {
            "provider": provider,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost": total_cost,
            "timestamp": self.last_tracked.isoformat()
        }
        
        logger.debug(f"Tracked {provider} usage: {input_tokens} input tokens, {output_tokens} output tokens, ${total_cost:.6f}")
        return usage_data
    
    def track_generic(self, 
                     provider: str,
                     model: str, 
                     input_tokens: int, 
                     output_tokens: int,
                     input_price: float,
                     output_price: float,
                     response_metadata: Optional[Dict] = None) -> Dict:
        """
        Track token usage for any model provider with custom pricing.
        
        Args:
            provider: The model provider name
            model: The model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            input_price: Price per 1K input tokens
            output_price: Price per 1K output tokens
            response_metadata: Optional response metadata from the API
            
        Returns:
            Dictionary with usage information
        """
        if provider not in self.usage:
            self.usage[provider] = {"input_tokens": 0, "output_tokens": 0, "cost": 0.0, "calls": 0}
        
        # Calculate cost
        input_cost = (input_tokens / 1000) * input_price
        output_cost = (output_tokens / 1000) * output_price
        total_cost = input_cost + output_cost
        
        # Update usage
        self.usage[provider]["input_tokens"] += input_tokens
        self.usage[provider]["output_tokens"] += output_tokens
        self.usage[provider]["cost"] += total_cost
        self.usage[provider]["calls"] += 1
        
        # Update totals
        self.usage["total"]["input_tokens"] += input_tokens
        self.usage["total"]["output_tokens"] += output_tokens
        self.usage["total"]["cost"] += total_cost
        self.usage["total"]["calls"] += 1
        
        self.last_tracked = datetime.now()
        
        usage_data = {
            "provider": provider,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost": total_cost,
            "timestamp": self.last_tracked.isoformat()
        }
        
        logger.debug(f"Tracked {provider} usage: {input_tokens} input tokens, {output_tokens} output tokens, ${total_cost:.6f}")
        return usage_data
    
    def get_usage_report(self, provider: Optional[str] = None) -> Dict:
        """
        Get the current usage report.
        
        Args:
            provider: Optional provider to filter results
            
        Returns:
            Dictionary with usage information
        """
        if provider and provider in self.usage:
            return {
                provider: self.usage[provider],
                "session_start": self.session_start.isoformat(),
                "session_duration": str(datetime.now() - self.session_start)
            }
        
        return {
            "usage": self.usage,
            "session_start": self.session_start.isoformat(),
            "session_duration": str(datetime.now() - self.session_start)
        }
    
    def print_usage_report(self, provider: Optional[str] = None):
        """Print a formatted usage report."""
        report = self.get_usage_report(provider)
        
        print("\n===== TOKEN USAGE REPORT =====")
        print(f"Session started: {self.session_start.isoformat()}")
        print(f"Session duration: {datetime.now() - self.session_start}")
        print("==============================")
        
        if provider:
            usage = report[provider]
            print(f"Provider: {provider}")
            print(f"Input tokens: {usage['input_tokens']}")
            print(f"Output tokens: {usage['output_tokens']}")
            print(f"Total tokens: {usage['input_tokens'] + usage['output_tokens']}")
            print(f"Total cost: ${usage['cost']:.6f}")
            print(f"Number of API calls: {usage['calls']}")
        else:
            for provider, usage in report["usage"].items():
                if provider == "total":
                    continue
                
                if usage["calls"] > 0:
                    print(f"\nProvider: {provider}")
                    print(f"Input tokens: {usage['input_tokens']}")
                    print(f"Output tokens: {usage['output_tokens']}")
                    print(f"Total tokens: {usage['input_tokens'] + usage['output_tokens']}")
                    print(f"Total cost: ${usage['cost']:.6f}")
                    print(f"Number of API calls: {usage['calls']}")
            
            print("\n======= TOTAL USAGE =======")
            total = report["usage"]["total"]
            print(f"Total input tokens: {total['input_tokens']}")
            print(f"Total output tokens: {total['output_tokens']}")
            print(f"Total tokens: {total['input_tokens'] + total['output_tokens']}")
            print(f"Total cost: ${total['cost']:.6f}")
            print(f"Total API calls: {total['calls']}")
    
    def save_report_to_file(self, filename: Optional[str] = None) -> str:
        """
        Save the usage report to a JSON file.
        
        Args:
            filename: Optional filename to save to
            
        Returns:
            Path to the saved file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"token_usage_report_{timestamp}.json"
        
        report = self.get_usage_report()
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Usage report saved to {filename}")
        return filename
    
    def reset(self):
        """Reset the tracker to start a new session."""
        self.usage = {
            "openai": {"input_tokens": 0, "output_tokens": 0, "cost": 0.0, "calls": 0},
            "anthropic": {"input_tokens": 0, "output_tokens": 0, "cost": 0.0, "calls": 0},
            "deepseek": {"input_tokens": 0, "output_tokens": 0, "cost": 0.0, "calls": 0},
            "xai": {"input_tokens": 0, "output_tokens": 0, "cost": 0.0, "calls": 0},
            "total": {"input_tokens": 0, "output_tokens": 0, "cost": 0.0, "calls": 0}
        }
        
        self.session_start = datetime.now()
        self.last_tracked = None
        logger.info("Token tracker reset")


# Global instance for easy import and use
token_tracker = TokenTracker()

# Example usage
if __name__ == "__main__":
    # Example tracking for different providers
    token_tracker.track_openai("gpt-4o", 1000, 500)
    token_tracker.track_anthropic("claude-3-sonnet", 1500, 750)
    token_tracker.track_deepseek("deepseek-chat", 800, 400)
    token_tracker.track_xai("grok-1", 1200, 600)
    
    # Print report
    token_tracker.print_usage_report()
    
    # Save to file
    token_tracker.save_report_to_file() 