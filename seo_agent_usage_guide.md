# SEO Agent Usage Guide

## Prerequisites

- Python 3.11+
- API keys for all models:
  - OpenAI (for O3Mini)
  - Anthropic (for Claude)
  - DeepSeek
  - xAI (for Grok)

## Installation

1. Install required packages:

```bash
pip install agno>=1.2.6
pip install python-dotenv
pip install fastapi uvicorn
pip install duckduckgo-search
```

Alternatively, use the requirements.txt file:

```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your API keys:

```
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
DEEPSEEK_API_KEY=your_deepseek_key
XAI_API_KEY=your_xai_key  # This is needed for Grok
```

## Testing Sequence

Run these commands in order to test each component:

### 1. Test Individual Model Access

```bash
python3 test_models.py
```

This verifies your API keys work with each model provider.

### 2. Test Grok's Real-Time Data Capabilities 

```bash
python3 test_grok_realtime.py
```

This tests the structured data retrieval with Grok's internet access.

### 3. Run the Integration Test

```bash
python3 test_integration.py
```

This tests the full workflow with all models in sequence:
- Research with O3Mini
- Brief creation with DeepSeek
- Facts collection with Grok
- Content creation with Claude

### 4. Run the API Server

```bash
python3 api.py
```

The API will be available at http://localhost:8000

## API Usage

In a separate terminal, test the API:

```bash
# Create content
curl -X POST "http://localhost:8000/api/v1/content" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "sustainable travel trends 2025",
    "content_type": "blog post",
    "tone": "informative",
    "word_count": 500
  }'

# Check status (replace with actual workflow_id)
curl "http://localhost:8000/api/v1/workflows/12345678-1234-5678-1234-567812345678"
```

## Troubleshooting

- If DuckDuckGo search isn't working, reinstall with:
  ```bash
  pip install --force-reinstall duckduckgo-search
  ```

- Check your API keys are correctly set in the `.env` file. Note that for Grok, the environment variable should be XAI_API_KEY as shown in the agno_config.py file.

- Ensure Agno version is 1.2.6 or higher:
  ```bash
  pip show agno
  ``` 