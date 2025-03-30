# Agno Framework Integration

## Overview

The SEO Agent integrates the Agno agent framework (version 1.2.6+) to orchestrate multiple specialized language models in a coordinated workflow. This document outlines how Agno is configured and utilized throughout the application.

## Core Components

### Configuration

The `agno_config.py` module handles the initialization and configuration of the Agno framework:

- **Storage Providers**: Configures either PostgreSQL or in-memory storage
- **Knowledge Providers**: Enables PGVector for semantic search when available
- **API Keys**: Sets environment variables for various model providers (OpenAI, Anthropic, DeepSeek, Grok)

### Agent Models

Each agent uses a specialized model tailored to its specific task:

- **Research Agent**: Uses OpenAI's O3-mini model for processing large volumes of content
- **Brief Agent**: Uses DeepSeek for gap analysis and content planning
- **Facts Agent**: Uses Grok 3 for gathering factual information
- **Content Agent**: Uses Claude 3.7 for generating polished content

### Storage System

The storage system persists agent state and workflow data:

- **PostgreSQL Storage**: Production-ready persistent storage
- **Memory Storage**: Lightweight fallback for development or testing (with `dir_path` parameter)
- **State Management**: Maintains agent session data between runs

### Knowledge Base

The knowledge base caches research results for reuse:

- **PGVector**: Vector database for semantic search capabilities
- **Embeddings**: Stores text with vector representations for similarity search
- **Metadata**: Preserves structured data alongside text content

## Configuration Settings

Key settings that control Agno behavior:

| Setting | Description | Default |
|---------|-------------|---------|
| `USE_POSTGRES_STORAGE` | Use PostgreSQL for storage | `true` |
| `PGVECTOR_ENABLED` | Enable vector database for knowledge | `false` |
| `TEAM_ORCHESTRATION` | Execution mode (sequential/parallel) | `sequential` |
| `KNOWLEDGE_PROVIDER` | Provider type for knowledge base | `pg_vector` |
| `KNOWLEDGE_COLLECTION` | Collection name for storing data | `seo_agent_knowledge` |

## Usage Patterns

### Initializing Agno

Agno is initialized at application startup:

```python
from src.config.agno_config import init_agno

# Initialize Agno framework
init_agno()
```

### Creating Agents

Agents are initialized with proper models and storage:

```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from src.config.agno_config import get_storage, get_knowledge_provider

class MyAgent(Agent):
    def __init__(self, storage=None):
        super().__init__(
            name="Agent Name",
            description="Agent description",
            model=OpenAIChat(id="gpt-4o"),
            storage=storage or get_storage(),
            knowledge=get_knowledge_provider()
        )
```

### Model-Specific Initialization

Each model type has its own initialization pattern:

```python
# OpenAI
from agno.models.openai import OpenAIChat
model = OpenAIChat(id="gpt-4o")

# Anthropic/Claude
from agno.models.anthropic import Claude
model = Claude(id="claude-3-7-sonnet-20240307")

# DeepSeek (via Custom model)
from agno.models.custom import Custom
model = Custom(
    id="deepseek-large",
    config={
        "base_url": "https://api.deepseek.com/v1",
        "api_key": api_key,
        "request_mapping": {
            # Configuration for API mapping
        }
    }
)
```

### Running Workflow

The workflow orchestrates multiple agents:

```python
from agno import Team, Context

# Create team with agents
team = Team(
    name="My Team",
    agents=[agent1, agent2, agent3],
    orchestration=TeamOrchestration.SEQUENTIAL,
    storage=storage_provider
)

# Execute team with shared context
result = await team.run(context)
```

## Best Practices

1. **Direct Model Initialization**: Initialize models directly with their respective classes
2. **Global Storage Provider**: Access storage through `get_storage()` to ensure consistent configuration
3. **Session Management**: Use agent sessions to cache intermediate results
4. **Context Validation**: Validate context data before agent execution
5. **Knowledge Reuse**: Check knowledge store before performing expensive operations

## Limitations and Considerations

- **API Compatibility**: Agno 1.2.6+ has a different API than previous versions
- **Rate Limits**: Be aware of API rate limits when using multiple LLMs
- **Stateful Operations**: Agent execution is stateful and requires proper cleanup
- **Context Size**: Large contexts may exceed model token limits
- **Cost Management**: Different models have different pricing structures

## Troubleshooting

Common issues and their solutions:

1. **Storage Connection Errors**: Check PostgreSQL connection parameters
2. **Knowledge Provider Failures**: Ensure PGVector extension is installed 
3. **Agent Timeouts**: Adjust timeout settings or reduce batch sizes
4. **Context Overflow**: Limit input data size or use chunking strategies
5. **Import Errors**: Ensure correct import paths for Agno 1.2.6+ (`agno.models.openai` instead of `agno.models`)
6. **Model Initialization**: Check that model initialization follows the updated pattern with `id` instead of `model_name` 