# SEO Agent Tests

This directory contains tests for the SEO Agent system organized by functionality:

## Directory Structure

- `integration/`: End-to-end integration tests for the complete content creation workflow
- `models/`: Tests for individual model connections (OpenAI, Anthropic, DeepSeek, xAI/Grok)
- `tools/`: Tests for various tools including search capabilities and real-time data fetching
- `utils/`: Utility tests and debugging helpers

## Running Tests

To run individual tests:

```bash
# Run a specific test
python tests/integration/test_integration_agno.py

# Run model tests
python tests/models/test_models.py
```

## Test Organization

Tests are organized by functionality to make it easier to maintain and extend the test suite. When adding new tests, please follow this structure:

1. **Integration Tests**: Full workflow tests that exercise multiple components
2. **Model Tests**: Tests for specific model providers and their capabilities
3. **Tool Tests**: Tests for auxiliary tools like search and data retrieval
4. **Utility Tests**: Helpers for monitoring, debugging, and diagnostics

## API Keys

Tests require API keys for various LLM providers. Make sure your `.env` file includes:

```
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...
DEEPSEEK_API_KEY=...
XAI_API_KEY=...  # For Grok
``` 