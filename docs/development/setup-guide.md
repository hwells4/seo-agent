# Development Setup Guide

This guide provides detailed instructions for setting up and extending the Multi-LLM Agentic Content Creation System.

## Project Overview

We've built a scalable, multi-LLM content creation system using Agno as the agent framework and FastAPI for the API layer. The system follows a modular architecture with clear separation of concerns:

- **Agents**: Specialized LLM agents for research, brief creation, fact acquisition, and content generation
- **Services**: Middleware connecting agents, LLMs, and the API layer
- **Models**: Data structures for requests, responses, and internal representations
- **API**: RESTful endpoints for interacting with the system
- **Utils**: Shared utilities for error handling, validation, etc.

## Current Implementation Status

The project has the following components implemented:

- ✅ Project structure and file organization
- ✅ Configuration management system
- ✅ Data models for workflow and content
- ✅ LLM service for interacting with different models
- ✅ Research Agent implementation (O3Mini)
- ✅ Workflow orchestration service
- ✅ API endpoints for content generation
- ✅ Error handling and validation utilities
- ✅ Docker and Railway.app deployment configuration

## Next Implementation Steps

To complete the system, implement the remaining agents:

1. **Brief Agent (DeepSeek)**
   - Create `src/agents/brief_agent.py` based on the Research Agent pattern
   - Implement logic to process research results and generate content briefs
   - Use DeepSeek model for gap analysis and brief creation

2. **Facts Agent (Grok3)**
   - Create `src/agents/facts_agent.py` 
   - Implement logic to collect real-time facts and data
   - Leverage Grok3's web access capabilities

3. **Content Agent (Claude 3.7)**
   - Create `src/agents/content_agent.py`
   - Implement logic to generate high-quality content based on brief and facts
   - Use Claude 3.7 for final content generation

4. **Human-in-the-Loop Integration**
   - Enhance the Workflow Service with human review capabilities
   - Add endpoints for submitting and processing feedback

## Agent Implementation Pattern

Follow this pattern when implementing each agent:

1. Define the agent class extending Agno's `Agent` base class:
   ```python
   class BriefAgent(Agent):
       def __init__(self):
           super().__init__(
               name="Brief Agent",
               description="Creates content briefs based on research analysis.",
               model=llm_service.models["deepseek-large"]
           )
   ```

2. Implement context validation:
   ```python
   async def validate_context(self, context: Context) -> bool:
       # Validate that the context contains required data
       if not context.get("research_output"):
           logger.error("Missing research output in context")
           return False
       return True
   ```

3. Implement the main run method:
   ```python
   async def run(self, context: Context) -> Dict[str, Any]:
       # Start timing execution
       start_time = time.time()
       
       # Validate context
       if not await self.validate_context(context):
           raise ValueError("Invalid context for brief agent")
           
       # Core agent logic goes here
       # ...
       
       # Return structured output
       return brief_output.dict()
   ```

4. Add helper methods for breaking down complex logic:
   ```python
   async def _identify_content_gaps(self, research_output: Dict[str, Any]) -> List[Dict[str, Any]]:
       # Helper method for specific task
       # ...
   ```

## Testing Your Implementation

1. Unit testing individual agents:
   ```bash
   pytest tests/agents/test_brief_agent.py
   ```

2. Testing the entire workflow:
   ```bash
   pytest tests/services/test_workflow_service.py
   ```

3. Manual testing via API:
   ```bash
   curl -X POST http://localhost:8000/api/v1/workflows \
     -H "Content-Type: application/json" \
     -H "X-API-Key: your-api-key" \
     -d '{"keyword": "test keyword", "content_type": "blog post"}'
   ```

## Documentation

As you implement new components, update the following documentation:

- `docs/architecture/`: System design and component relationships
- `docs/features/`: User-facing feature documentation
- `docs/systems/`: Internal system documentation
- `tests/`: Test cases and examples

## Best Practices

- Follow Cursor rules for code style and quality checks
- Use type hints throughout your code
- Add comprehensive docstrings
- Handle errors appropriately
- Validate inputs and outputs
- Avoid hardcoding credentials
- Use async patterns consistently 