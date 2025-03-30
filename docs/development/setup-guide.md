# Development Setup Guide

This guide provides detailed instructions for setting up and extending the Multi-LLM Agentic Content Creation System.

## Project Overview

We've built a scalable, multi-LLM content creation system using Agno 1.2.6+ as the agent framework and FastAPI for the API layer. The system follows a modular architecture with clear separation of concerns:

- **Agents**: Specialized LLM agents for research, brief creation, fact acquisition, and content generation
- **Services**: Middleware connecting agents and the API layer
- **Models**: Data structures for requests, responses, and internal representations
- **API**: RESTful endpoints for interacting with the system
- **Utils**: Shared utilities for error handling, validation, etc.

## Current Implementation Status

The project has the following components implemented:

- ✅ Project structure and file organization
- ✅ Configuration management system
- ✅ Data models for workflow and content
- ✅ Agno framework integration (version 1.2.6+)
- ✅ Research Agent implementation (OpenAI)
- ✅ Brief Agent implementation (DeepSeek)
- ✅ Facts Agent implementation (Grok)
- ✅ Content Agent implementation (Claude)
- ✅ Workflow orchestration service
- ✅ API endpoints for content generation
- ✅ Error handling and validation utilities
- ✅ FastAPI application structure

## Dependencies

The application requires the following dependencies:

1. **Python 3.11+**
2. **API Keys** for various LLM providers:
   - OpenAI API key
   - Anthropic API key
   - DeepSeek API key
   - Grok API key
3. **Client Libraries**:
   - `openai` (v1.69.0+)
   - `anthropic`
   - `openrouter`
   - `grok-api`
4. **Agno Framework** (v1.2.6+)
5. **FastAPI**
6. **Pydantic** (v2.0+)

## Environment Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/seo-agent.git
   cd seo-agent
   ```

2. **Create and activate a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create .env file with API keys**
   ```
   OPENAI_API_KEY=sk-...
   ANTHROPIC_API_KEY=sk-...
   DEEPSEEK_API_KEY=sk-...
   GROK_API_KEY=sk-...
   EMAIL_TO='[]'
   ```

## Agent Implementation Pattern

All agents are already implemented following this pattern:

1. Define the agent class extending Agno's `Agent` base class:
   ```python
   from agno.agent import Agent
   from agno.models.openai import OpenAIChat
   
   class ResearchAgent(Agent):
       def __init__(self, storage=None):
           super().__init__(
               name="Research Agent",
               description="Analyzes existing content for a target keyword.",
               model=OpenAIChat(id="gpt-4o"),
               storage=storage,
               knowledge=get_knowledge_provider()
           )
   ```

2. Implement context validation:
   ```python
   async def validate_context(self, context: Dict[str, Any]) -> bool:
       # Validate that the context contains required information
       if not context.get("keyword"):
           logger.error("Missing required keyword in context")
           return False
       return True
   ```

3. Implement the main run method:
   ```python
   async def run(self, context: Dict[str, Any] = None) -> Dict[str, Any]:
       # Use the context passed or the agent's own context
       context = context or self.context
       
       # Start timing execution
       start_time = time.time()
       
       # Validate context
       if not await self.validate_context(context):
           raise ValueError("Invalid context for research agent")
       
       # ... Agent logic ...
       
       return research_output.dict()
   ```

## Running the Application

To run the application:

```bash
python -m src.main
```

This starts the FastAPI application on http://localhost:8000. You can access:
- API documentation at http://localhost:8000/docs
- ReDoc at http://localhost:8000/redoc
- Health check at http://localhost:8000/api/v1/health

## Testing

1. Unit testing:
   ```bash
   pytest tests/
   ```

2. Manual testing via API:
   ```bash
   curl -X POST http://localhost:8000/api/v1/workflows \
     -H "Content-Type: application/json" \
     -H "X-API-Key: your-api-key" \
     -d '{"keyword": "best ergonomic chairs", "content_type": "blog post"}'
   ```

## Troubleshooting

Common issues and solutions:

1. **Import Errors**: Ensure you're using the correct import paths for Agno 1.2.6+:
   - Use `from agno.models.openai import OpenAIChat` not `from agno.models import OpenAI`
   - Use `from agno.models.anthropic import Claude` not `from agno.models import Anthropic`

2. **API Key Issues**: Verify all API keys are correctly set in the .env file

3. **Model Initialization**: Models require the `id` parameter, not `model_name`

4. **Storage Errors**: If using PostgreSQL, verify the database connection details

## Documentation

For more information, refer to:

- `docs/architecture/`: System design and component relationships
- `docs/features/`: User-facing feature documentation
- `docs/systems/`: Internal system documentation (see `agno-integration.md` for details)
- `docs/development/`: Development guides and practices 