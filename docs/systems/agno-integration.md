# Agno Framework Integration

## Overview

The SEO Agent integrates the Agno agent framework to orchestrate multiple specialized language models in a coordinated workflow. This document outlines how Agno is configured and utilized throughout the application.

## Core Components

### Configuration

The `agno_config.py` module handles the initialization and configuration of the Agno framework:

- **Storage Providers**: Configures either PostgreSQL or in-memory storage
- **Knowledge Providers**: Enables PGVector for semantic search when available
- **Model Parameters**: Sets default timeouts and other shared parameters

### Agent Orchestration

Agents are structured in a team with either sequential or parallel execution:

- **Sequential Mode**: Each agent runs after the previous one completes
- **Parallel Mode**: Multiple agents can run concurrently when appropriate
- **Context Passing**: Shared context enables data flow between agents

### Storage System

The storage system persists agent state and workflow data:

- **PostgreSQL Storage**: Production-ready persistent storage
- **Memory Storage**: Lightweight fallback for development or testing
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
from agno import Agent
from src.config.agno_config import get_knowledge_provider

class MyAgent(Agent):
    def __init__(self, storage=None):
        super().__init__(
            name="Agent Name",
            description="Agent description",
            model=llm_service.models["model_key"],
            storage=storage,
            knowledge=get_knowledge_provider()
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

1. **Error Handling**: Always include proper error handling and fallbacks
2. **Session Management**: Use agent sessions to cache intermediate results
3. **Context Validation**: Validate context data before agent execution
4. **Knowledge Reuse**: Check knowledge store before performing expensive operations
5. **Storage Configuration**: Properly configure storage based on environment

## Limitations and Considerations

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