# SEO Agent System

A scalable, modular system for SEO-optimized content creation using specialized AI agents. Each agent in the pipeline is optimized for a specific task in the content creation process.

## Features

- SEO content creation with a sequential pipeline of specialized AI agents
- Each agent is optimized for its specific role:
  - Research Engine (O3Mini) for analyzing content structures and patterns
  - Brief Creator (DeepSeek) for strategic content planning and gap analysis
  - Facts Collector (Grok) for gathering up-to-date facts and statistics
  - Content Creator (Claude 3.7) for producing high-quality content
- RESTful API for convenient access to the content creation pipeline
- Flexible architecture that allows for adding additional agent types

## Project Structure

```
seo-agent/
├── agents/                   # Main agent pipelines
│   ├── content/              # Content creation pipeline
│   │   ├── __init__.py
│   │   └── pipeline.py       # Content creation implementation
│   └── template/             # Template for creating new agent types
│       ├── __init__.py
│       └── pipeline.py       # Example implementation
│
├── api/                      # API modules
│   ├── __init__.py
│   ├── base.py               # Main FastAPI app
│   └── routers/              # API endpoint routers
│       ├── __init__.py
│       └── content.py        # Content creation endpoints
│
├── docs/                     # Documentation
│   ├── getting_started.md
│   ├── architecture/
│   ├── features/
│   └── development/
│
├── tests/                    # Tests
│   ├── integration/
│   └── unit/
│
├── content_storage/          # Storage for agent outputs
├── .env                      # Environment variables (API keys)
├── run_server.py             # Script to run the API server
└── requirements.txt          # Project dependencies
```

## Getting Started

See the [Getting Started Guide](docs/getting_started.md) for detailed setup and usage instructions.

### Quick Start

1. Set up environment:
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

2. Configure API keys:
```bash
cp .env.example .env
# Edit .env to add your API keys
```

3. Run the API server:
```bash
python run_server.py
# API will be available at http://localhost:8000
```

4. Access the API:
```bash
# Create content
curl -X 'POST' \
  'http://localhost:8000/api/v1/content' \
  -H 'Content-Type: application/json' \
  -d '{
    "topic": "container gardening tips",
    "content_type": "blog post",
    "tone": "helpful",
    "word_count": 800
  }'

# Check workflow status
curl -X 'GET' 'http://localhost:8000/api/v1/workflows/{workflow_id}'
```

## Documentation

- [Getting Started Guide](docs/getting_started.md)
- [Architecture Overview](docs/architecture/sequential-pipeline.md)
- [Content Pipeline Documentation](docs/features/content_pipeline.md)
- [Contributing Guide](docs/development/contributing.md)

## Adding New Agent Types

To add a new agent type:

1. Copy the `agents/template` directory to `agents/your_agent_type`
2. Customize the pipeline implementation in `agents/your_agent_type/pipeline.py`
3. Update the `__init__.py` to export the necessary functions
4. Create a new router in `api/routers/your_agent_type.py`
5. Include the router in `api/base.py`

## License

This project is licensed under the MIT License - see the LICENSE file for details.
