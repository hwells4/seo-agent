import os
import json
import tiktoken
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
    
    # Default token prices per 1000 tokens (input, output) as of June 2024
    DEFAULT_PRICES = {
        "openai": {
            "gpt-3.5-turbo": (0.0005, 0.0015),    # $0.0005 per 1K input, $0.0015 per 1K output
            "gpt-4o": (0.005, 0.015),             # $0.005 per 1K input, $0.015 per 1K output
            "gpt-4-turbo": (0.01, 0.03),          # $0.01 per 1K input, $0.03 per 1K output
            "gpt-4": (0.03, 0.06),                # $0.03 per 1K input, $0.06 per 1K output
        },
        "anthropic": {
            "claude-3-sonnet": (0.003, 0.015),    # $0.003 per 1K input, $0.015 per 1K output
            "claude-3-sonnet-20240229": (0.003, 0.015),  # $0.003 per 1K input, $0.015 per 1K output
            "claude-3-opus": (0.015, 0.075),      # $0.015 per 1K input, $0.075 per 1K output
            "claude-3-haiku": (0.00025, 0.00125), # $0.00025 per 1K input, $0.00125 per 1K output
            "claude-3.5-sonnet": (0.003, 0.015),  # $0.003 per 1K input, $0.015 per 1K output
            "claude-3.7-sonnet": (0.003, 0.015)   # $0.003 per 1K input, $0.015 per 1K output (Claude 3.7 pricing)
        },
        "deepseek": {
            "deepseek-chat": (0.00027, 0.0011),   # $0.27 per 1M input, $1.10 per 1M output (converted to per 1K)
            "deepseek-reasoner": (0.00055, 0.00219) # $0.55 per 1M input, $2.19 per 1M output (converted to per 1K)
        },
        "xai": {
            "grok-1": (0.0005, 0.0015),           # Estimated pricing (no official API pricing yet)
        },
        "openrouter": {
            "o3-mini": (0.0015, 0.002),           # $0.0015 per 1K input, $0.002 per 1K output
            "o3-preview": (0.003, 0.004),         # $0.003 per 1K input, $0.004 per 1K output
            "gpt-4o": (0.005, 0.015),             # $0.005 per 1K input, $0.015 per 1K output
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
            "openrouter": {"input_tokens": 0, "output_tokens": 0, "cost": 0.0, "calls": 0},
            "total": {"input_tokens": 0, "output_tokens": 0, "cost": 0.0, "calls": 0}
        }
        
        # Track per-step usage
        self.step_usage = {}
        
        self.prices = self.DEFAULT_PRICES.copy()
        if custom_prices:
            self._update_prices(custom_prices)
        
        self.session_start = datetime.now()
        self.last_tracked = None
        
        # Initialize tokenizers
        self._tokenizers = {}
    
    def _update_prices(self, custom_prices: Dict):
        """Update the pricing dictionary with custom values."""
        for provider, models in custom_prices.items():
            if provider not in self.prices:
                self.prices[provider] = {}
            
            for model, price in models.items():
                self.prices[provider][model] = price
    
    def _get_tokenizer(self, model_name: str):
        """Get the appropriate tokenizer for the model."""
        if model_name in self._tokenizers:
            return self._tokenizers[model_name]
        
        # OpenAI models
        if "gpt-4" in model_name or "gpt-3.5" in model_name:
            tokenizer = tiktoken.encoding_for_model(model_name)
        # Default to cl100k_base for other models
        else:
            tokenizer = tiktoken.get_encoding("cl100k_base")
        
        self._tokenizers[model_name] = tokenizer
        return tokenizer
    
    def estimate_tokens(self, text: str, model_name: str = "gpt-3.5-turbo") -> int:
        """Estimate the number of tokens in the given text."""
        if not text:
            return 0
            
        try:
            tokenizer = self._get_tokenizer(model_name)
            return len(tokenizer.encode(text))
        except Exception as e:
            logger.warning(f"Error estimating tokens: {e}")
            # Fallback: rough estimate based on whitespace tokens
            return len(text) // 4
    
    def track_step(self, 
                  step_name: str,
                  provider: str,
                  model: str, 
                  input_text: str,
                  output_text: str):
        """
        Track token usage for a specific pipeline step.
        
        Args:
            step_name: Name of the pipeline step
            provider: The model provider (openai, anthropic, etc.)
            model: The model name
            input_text: Input text sent to the model
            output_text: Output text received from the model
        """
        # Estimate tokens
        input_tokens = self.estimate_tokens(input_text, model)
        output_tokens = self.estimate_tokens(output_text, model)
        
        # Track based on provider
        usage_data = None
        if provider == "openai":
            usage_data = self.track_openai(model, input_tokens, output_tokens)
        elif provider == "anthropic":
            usage_data = self.track_anthropic(model, input_tokens, output_tokens)
        elif provider == "deepseek":
            usage_data = self.track_deepseek(model, input_tokens, output_tokens)
        elif provider == "xai":
            usage_data = self.track_xai(model, input_tokens, output_tokens)
        elif provider == "openrouter":
            usage_data = self.track_openrouter(model, input_tokens, output_tokens)
        else:
            # Default to generic tracking with estimated pricing
            usage_data = self.track_generic(
                provider, model, input_tokens, output_tokens, 
                input_price=0.001, output_price=0.002
            )
        
        # Store step usage data
        if step_name not in self.step_usage:
            self.step_usage[step_name] = []
        
        self.step_usage[step_name].append(usage_data)
        
        logger.info(f"Step {step_name}: Tracked {provider} ({model}): {input_tokens} input, {output_tokens} output tokens")
        return usage_data
    
    def track_openai(self, 
                    model: str, 
                    input_tokens: int, 
                    output_tokens: int) -> Dict:
        """
        Track token usage for OpenAI models.
        
        Args:
            model: The OpenAI model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
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
                       output_tokens: int) -> Dict:
        """
        Track token usage for Anthropic Claude models.
        
        Args:
            model: The Claude model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
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
                      output_tokens: int) -> Dict:
        """
        Track token usage for DeepSeek models.
        
        Args:
            model: The DeepSeek model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
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
                 output_tokens: int) -> Dict:
        """
        Track token usage for xAI Grok models.
        
        Args:
            model: The Grok model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
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
    
    def track_openrouter(self, 
                       model: str, 
                       input_tokens: int, 
                       output_tokens: int) -> Dict:
        """
        Track token usage for OpenRouter models.
        
        Args:
            model: The OpenRouter model name (e.g., 'o3-mini', 'gpt-4o')
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Dictionary with usage information
        """
        provider = "openrouter"
        
        # Get pricing
        model_key = model.split('/')[-1] if '/' in model else model
        model_prices = self.prices[provider].get(
            model_key, 
            self.prices[provider].get("o3-mini")  # Default fallback
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
                     output_price: float) -> Dict:
        """
        Track token usage for any model provider with custom pricing.
        
        Args:
            provider: The model provider name
            model: The model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            input_price: Price per 1K input tokens
            output_price: Price per 1K output tokens
            
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
        
        report = {
            "usage": self.usage,
            "step_usage": self.step_usage,
            "session_start": self.session_start.isoformat(),
            "session_duration": str(datetime.now() - self.session_start)
        }
        
        return report
    
    def print_usage_report(self, provider: Optional[str] = None):
        """Print a formatted usage report."""
        report = self.get_usage_report(provider)
        
        print("\n===== TOKEN USAGE REPORT =====")
        print(f"Session started: {self.session_start.isoformat()}")
        print(f"Session duration: {datetime.now() - self.session_start}")
        
        # Print provider-specific usage
        for provider_name, provider_data in report["usage"].items():
            if provider_name != "total":
                cost = provider_data["cost"]
                calls = provider_data["calls"]
                input_tokens = provider_data["input_tokens"]
                output_tokens = provider_data["output_tokens"]
                
                if calls > 0:
                    print(f"\n{provider_name.upper()}:")
                    print(f"  Calls: {calls}")
                    print(f"  Input tokens: {input_tokens:,}")
                    print(f"  Output tokens: {output_tokens:,}")
                    print(f"  Total tokens: {input_tokens + output_tokens:,}")
                    print(f"  Cost: ${cost:.4f}")
        
        # Print totals
        total_data = report["usage"]["total"]
        print("\nTOTAL USAGE:")
        print(f"  Calls: {total_data['calls']}")
        print(f"  Input tokens: {total_data['input_tokens']:,}")
        print(f"  Output tokens: {total_data['output_tokens']:,}")
        print(f"  Total tokens: {total_data['input_tokens'] + total_data['output_tokens']:,}")
        print(f"  Total cost: ${total_data['cost']:.4f}")
        
        # Print step usage
        if "step_usage" in report and report["step_usage"]:
            print("\nUSAGE BY STEP:")
            
            for step_name, step_data in report["step_usage"].items():
                step_total_cost = sum(item["total_cost"] for item in step_data)
                step_total_tokens = sum(item["input_tokens"] + item["output_tokens"] for item in step_data)
                
                print(f"\n  {step_name}:")
                print(f"    Calls: {len(step_data)}")
                print(f"    Total tokens: {step_total_tokens:,}")
                print(f"    Cost: ${step_total_cost:.4f}")
                
                # Print model breakdown within this step
                models = {}
                for item in step_data:
                    model_key = f"{item['provider']}:{item['model']}"
                    if model_key not in models:
                        models[model_key] = {
                            "calls": 0,
                            "total_tokens": 0,
                            "cost": 0.0
                        }
                    
                    models[model_key]["calls"] += 1
                    models[model_key]["total_tokens"] += item["input_tokens"] + item["output_tokens"]
                    models[model_key]["cost"] += item["total_cost"]
                
                for model_key, model_data in models.items():
                    print(f"      {model_key}:")
                    print(f"        Calls: {model_data['calls']}")
                    print(f"        Total tokens: {model_data['total_tokens']:,}")
                    print(f"        Cost: ${model_data['cost']:.4f}")
        
        print("==============================")
    
    def save_report_to_file(self, filename: Optional[str] = None) -> str:
        """
        Save the usage report to a file.
        
        Args:
            filename: Optional custom filename, defaults to 'token_usage_{timestamp}.json'
            
        Returns:
            The filename used
        """
        import datetime
        import os
        import json
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if not filename:
            # Create directory if it doesn't exist
            os.makedirs("storage/token_usage", exist_ok=True)
            filename = f"storage/token_usage/tokens_{timestamp}.json"
        
        report = self.get_usage_report()
        
        with open(filename, "w") as f:
            json.dump(report, f, indent=2)
            
        logger.info(f"Token usage report saved to {filename}")
        return filename
    
    def reset(self):
        """Reset the token tracker."""
        self.usage = {
            "openai": {"input_tokens": 0, "output_tokens": 0, "cost": 0.0, "calls": 0},
            "anthropic": {"input_tokens": 0, "output_tokens": 0, "cost": 0.0, "calls": 0},
            "deepseek": {"input_tokens": 0, "output_tokens": 0, "cost": 0.0, "calls": 0},
            "xai": {"input_tokens": 0, "output_tokens": 0, "cost": 0.0, "calls": 0},
            "openrouter": {"input_tokens": 0, "output_tokens": 0, "cost": 0.0, "calls": 0},
            "total": {"input_tokens": 0, "output_tokens": 0, "cost": 0.0, "calls": 0}
        }
        self.step_usage = {}
        self.session_start = datetime.now()
        self.last_tracked = None
        
        logger.info("Token tracker reset")


# Global instance for easy import and use
token_tracker = TokenTracker() 