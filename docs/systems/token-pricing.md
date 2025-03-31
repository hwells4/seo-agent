# Token Pricing Documentation

## Overview

The SEO Agent carefully tracks token usage across all LLM providers to manage costs and optimize performance. This document outlines the current token pricing structure, how token tracking is implemented, and strategies for cost management.

## Current Token Pricing (as of June 2024)

Below are the current token prices per 1,000 tokens for all supported LLM providers:

### OpenAI Models

| Model | Input Cost (per 1K tokens) | Output Cost (per 1K tokens) |
|-------|----------------------------|----------------------------|
| GPT-3.5 Turbo | $0.0005 | $0.0015 |
| GPT-4o | $0.005 | $0.015 |
| GPT-4 Turbo | $0.01 | $0.03 |
| GPT-4 | $0.03 | $0.06 |

### Anthropic Models

| Model | Input Cost (per 1K tokens) | Output Cost (per 1K tokens) |
|-------|----------------------------|----------------------------|
| Claude 3 Haiku | $0.00025 | $0.00125 |
| Claude 3 Sonnet | $0.003 | $0.015 |
| Claude 3.5 Sonnet | $0.003 | $0.015 |
| Claude 3 Opus | $0.015 | $0.075 |

### DeepSeek Models

| Model | Input Cost (per 1K tokens) | Output Cost (per 1K tokens) |
|-------|----------------------------|----------------------------|
| DeepSeek Chat | $0.00027 | $0.0011 |
| DeepSeek Reasoner | $0.00055 | $0.00219 |

### xAI Models

| Model | Input Cost (per 1K tokens) | Output Cost (per 1K tokens) |
|-------|----------------------------|----------------------------|
| Grok-1 | $0.0005 (est.) | $0.0015 (est.) |

### OpenRouter Models

| Model | Input Cost (per 1K tokens) | Output Cost (per 1K tokens) |
|-------|----------------------------|----------------------------|
| o3-mini | $0.0015 | $0.002 |
| o3-preview | $0.003 | $0.004 |
| gpt-4o | $0.005 | $0.015 |

## Token Tracking Implementation

Token tracking is implemented through the `TokenTracker` utility class located in `agents/utils/token_tracker.py`. This class:

1. Maintains up-to-date pricing for all supported models
2. Tracks token usage per provider and model
3. Calculates costs based on input and output tokens
4. Generates usage reports for billing and optimization

### Usage Example

```python
from agents.utils.token_tracker import TokenTracker

# Initialize token tracker
tracker = TokenTracker()

# Track OpenAI usage
tracker.track_openai(
    model="gpt-4o",
    input_tokens=500,
    output_tokens=750
)

# Track Anthropic usage  
tracker.track_anthropic(
    model="claude-3-sonnet",
    input_tokens=600,
    output_tokens=900
)

# Get usage report
report = tracker.get_usage_report()
print(f"Total cost: ${report['total']['cost']:.4f}")
```

## Customizing Token Pricing

Token prices can be customized by:

1. Updating the `DEFAULT_PRICES` dictionary in `token_tracker.py`
2. Providing custom prices when initializing the `TokenTracker`:

```python
custom_prices = {
    "openai": {
        "gpt-4o": (0.004, 0.012)  # Custom pricing
    }
}

tracker = TokenTracker(custom_prices=custom_prices)
```

## Cost Management Strategies

The SEO Agent employs several strategies to manage token costs:

1. **Model Selection**: Each task uses the most cost-effective model for its requirements
2. **Prompt Engineering**: Prompts are designed for efficiency to minimize token usage
3. **Context Caching**: Previously processed content is cached to avoid redundant processing
4. **Content Batching**: Processing content in batches when possible to optimize token usage
5. **Usage Monitoring**: Regular monitoring of token usage to identify optimization opportunities

## Reporting and Analytics

The system generates detailed token usage reports that include:

1. Per-provider token usage and costs
2. Per-model breakdown of input and output tokens
3. Session duration and API call counts
4. Cost estimates for different content workflows

These reports are saved to the specified output directory and can be used for billing and optimization analysis.

## Updating Token Prices

To update token prices:

1. Edit the `DEFAULT_PRICES` dictionary in `agents/utils/token_tracker.py`
2. Update the corresponding dictionary in `tests/utils/token_tracker.py`
3. Update this documentation to reflect the new pricing

Check the official provider pricing pages regularly:
- [OpenAI Pricing](https://openai.com/pricing)
- [Anthropic Pricing](https://www.anthropic.com/pricing)
- [DeepSeek Pricing](https://api-docs.deepseek.com/quick_start/pricing)

## Troubleshooting

If you encounter issues with token tracking:

1. Verify that the model name matches the expected format in the tracker
2. Check if custom pricing is applied correctly
3. Ensure that token counts are being passed correctly to tracking methods
4. Validate that the usage reports are being saved to the correct location

For additional assistance, refer to the system logs or contact the development team. 