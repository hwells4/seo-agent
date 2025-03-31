# Getting Started with SEO Agent

This guide will help you get started with the SEO Agent content creation system, which uses a sequential pipeline of specialized AI agents to generate high-quality, SEO-optimized content.

## Prerequisites

Before you begin, make sure you have:

1. Python 3.9+ installed
2. API keys for the following LLM providers:
   - OpenAI API key (for GPT models)
   - Anthropic API key (for Claude models)
   - DeepSeek API key
   - xAI API key (for Grok)
3. Git installed (optional, for cloning the repository)

## Installation

### Option 1: Local Installation

1. Clone the repository or download the source code:
   ```bash
   git clone https://github.com/yourusername/seo-agent.git
   cd seo-agent
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up your environment variables:
   ```bash
   export OPENAI_API_KEY="your-openai-api-key"
   export ANTHROPIC_API_KEY="your-anthropic-api-key"
   export DEEPSEEK_API_KEY="your-deepseek-api-key"
   export XAI_API_KEY="your-xai-api-key"
   ```

   On Windows:
   ```bash
   set OPENAI_API_KEY=your-openai-api-key
   set ANTHROPIC_API_KEY=your-anthropic-api-key
   set DEEPSEEK_API_KEY=your-deepseek-api-key
   set XAI_API_KEY=your-xai-api-key
   ```

### Option 2: Docker Installation

1. Make sure Docker and Docker Compose are installed on your system.

2. Create a `.env` file in the project root with your API keys:
   ```
   OPENAI_API_KEY=your-openai-api-key
   ANTHROPIC_API_KEY=your-anthropic-api-key
   DEEPSEEK_API_KEY=your-deepseek-api-key
   XAI_API_KEY=your-xai-api-key
   ```

3. Build and start the Docker container:
   ```bash
   docker-compose up --build
   ```

## Running the API Server

### Local Environment

Start the API server:
```bash
python run_server.py
```

The API will be available at http://localhost:8000

### Docker Environment

If you're using Docker, the API server will start automatically when you run `docker-compose up`.

## Using the SEO Agent

### Method 1: API Endpoints

Once the server is running, you can interact with the SEO Agent through its REST API:

1. **Create content** by sending a POST request to `/api/v1/content` with your content parameters:
   ```bash
   curl -X 'POST' \
     'http://localhost:8000/api/v1/content' \
     -H 'Content-Type: application/json' \
     -d '{
       "topic": "container gardening tips",
       "content_type": "blog post",
       "tone": "helpful",
       "word_count": 500
     }'
   ```

2. **Check workflow status** by sending a GET request to `/api/v1/workflows/{workflow_id}`:
   ```bash
   curl -X 'GET' 'http://localhost:8000/api/v1/workflows/your-workflow-id'
   ```

### Method 2: Direct Python Usage

You can also use the SEO Agent directly in your Python code:

```python
from agents.content import run_content_pipeline

# Run the content pipeline
results = run_content_pipeline(
    topic="container gardening tips",
    content_type="blog post",
    tone="helpful",
    word_count=500,
    save_results=True
)

# The final content is available in:
content = results["steps"]["content"]["output"]
print(content)
```

## Understanding the Pipeline

The SEO Agent uses a sequential pipeline of specialized agents:

1. **Research Engine** (O3Mini): Analyzes existing content to understand what works well for the topic
2. **Brief Creator** (DeepSeek): Creates a strategic content brief with gap analysis
3. **Facts Collector** (Grok): Gathers up-to-date facts and information
4. **Content Creator** (Claude 3.7): Produces the final content based on all inputs

Each agent is carefully selected for its strengths in its particular task. The pipeline processes each step in sequence, passing the output of each agent to the next.

## Testing

Run the integration tests to verify your setup:

```bash
python tests/integration/test_content_team_mini.py
```

This will run a minimal test of the content creation pipeline, using a test topic to verify that all agents are working correctly with minimal token usage.

## Quick Testing with the Test Script

To quickly test the API, you can use the included test script:

```bash
./test_api.sh
```

This script will:
1. Start the API server if it's not running
2. Submit a test content creation request
3. Monitor the workflow status
4. Display the final results
5. Save the results to the content_storage directory

## Next Steps

After setting up and verifying your SEO Agent:

1. Read the full [Usage Guide](../docs/seo_agent_usage_guide.md) for detailed information on all available options
2. Explore the API documentation by visiting http://localhost:8000/docs when the server is running
3. Check out example workflows in the `tests/integration` directory 