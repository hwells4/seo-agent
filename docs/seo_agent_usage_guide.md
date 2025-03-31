# SEO Agent Usage Guide

This guide explains how to use the SEO Agent content creation system to generate high-quality, SEO-optimized content.

## System Overview

The SEO Agent uses a pipeline of specialized AI agents that run sequentially to create content:

1. **Research Engine (O3Mini)**: Analyzes existing content on the topic to understand what works well
2. **Brief Creator (DeepSeek)**: Creates a strategic content brief with gap analysis
3. **Facts Collector (Grok)**: Gathers up-to-date supporting facts and figures
4. **Content Creator (Claude 3.7)**: Produces the final content based on all inputs

Each agent is specifically selected for its strengths in its particular task, creating a workflow that combines the best capabilities of multiple AI models.

## Implementation Approach: Sequential Pipeline vs. Team

Our implementation uses a sequential pipeline of individual agents rather than a Team orchestration approach. This provides several benefits:

1. **Better Control**: Each step is explicitly defined, with clear inputs and outputs
2. **Easier Debugging**: Issues can be isolated to specific agents or steps
3. **More Flexibility**: Agents can be easily swapped or modified independently 
4. **Transparent Data Flow**: It's clear how data passes from one agent to the next
5. **Simplified Implementation**: Less complex orchestration logic needed

## Using the API

### Creating Content

To create content, send a POST request to `/api/v1/content`:

```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/content' \
  -H 'Content-Type: application/json' \
  -d '{
    "topic": "container gardening tips",
    "content_type": "blog post",
    "tone": "helpful",
    "word_count": 500,
    "brand_voice": {
      "tone": "Friendly but professional",
      "style": "Direct and practical",
      "sentence_structure": "Mix of short and long sentences with active voice",
      "language": "Accessible to general audience",
      "taboo_words": ["obviously", "simply", "just", "clearly"]
    }
  }'
```

The response will include a workflow ID:

```json
{
  "workflow_id": "de006f9e-c21d-42ed-ad38-c2e0cd3f75b1",
  "status": "pending",
  "message": "Content creation started"
}
```

### Checking Status

To check the status of your content generation, send a GET request to `/api/v1/workflows/{workflow_id}`:

```bash
curl -X 'GET' 'http://localhost:8000/api/v1/workflows/de006f9e-c21d-42ed-ad38-c2e0cd3f75b1'
```

The response will include the status of your workflow and the generated content when completed:

```json
{
  "workflow_id": "de006f9e-c21d-42ed-ad38-c2e0cd3f75b1",
  "status": "completed",
  "request": {
    "topic": "container gardening tips",
    "content_type": "blog post",
    "tone": "helpful",
    "word_count": 500,
    "brand_voice": {
      "tone": "Friendly but professional",
      "style": "Direct and practical"
    }
  },
  "result": "Generated content...",
  "error": null,
  "steps": {
    "research": {"status": "completed", "output": "..."},
    "brief": {"status": "completed", "output": "...", "gap_analysis": "..."},
    "facts": {"status": "completed", "output": "..."},
    "content": {"status": "completed", "output": "..."}
  }
}
```

## Direct Usage in Python

You can also use the content creation pipeline directly in your Python code:

```python
from content_creation_team import run_content_pipeline

# Define brand voice (optional)
brand_voice = {
    "tone": "Friendly but professional",
    "style": "Direct and practical",
    "sentence_structure": "Mix of short and long sentences with active voice",
    "language": "Accessible to general audience",
    "taboo_words": ["obviously", "simply", "just", "clearly"],
    "persuasion": "Focus on benefits rather than features",
    "format": "Use headers and bullet points for scannability"
}

# Run the content pipeline
results = run_content_pipeline(
    topic="container gardening tips",
    brand_voice=brand_voice,
    word_count=500,
    save_results=True
)

# Access the results
research_output = results["steps"]["research"]["output"]
brief_output = results["steps"]["brief"]["output"]
gap_analysis = results["steps"]["brief"]["extracted_gap_analysis"]
facts_output = results["steps"]["facts"]["output"]
content_output = results["steps"]["content"]["output"]

print(content_output)
```

## Customization Options

### Brand Voice

You can customize the brand voice through these parameters:

- **tone**: Overall tone (e.g., "Professional", "Casual", "Authoritative")
- **style**: Writing style (e.g., "Direct", "Storytelling", "Educational")
- **sentence_structure**: How sentences are constructed (e.g., "Varied length", "Short and punchy")
- **language**: Language usage (e.g., "Technical", "Simple", "Industry terminology")
- **taboo_words**: Words to avoid in content (e.g., ["obviously", "simply", "just"])
- **persuasion**: Persuasion techniques (e.g., "Social proof", "Facts and statistics")
- **format**: Content formatting (e.g., "Headers and bullet points", "Numbered lists")

### Content Parameters

- **topic**: The main topic for content creation (required)
- **content_type**: Type of content ("blog post", "article", "guide", etc.)
- **tone**: Overall tone ("helpful", "authoritative", "friendly", etc.)
- **word_count**: Target word count for content (100-2000 words)

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