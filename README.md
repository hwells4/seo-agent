# Multi-LLM Agentic Content Creation System

A powerful content creation workflow system that leverages multiple specialized language models in a coordinated process to produce high-quality, SEO-optimized content. The system reduces 50-80 hours of manual content production work to approximately 30-40 minutes of automated processing with human quality assurance.

## Architecture

This system uses a multi-stage workflow involving different LLM models specialized for specific tasks:

1. **Research & Analysis Engine (O3Mini)**: Processes large volumes of existing content to understand topic coverage and competitive landscape.
2. **Gap Analysis & Brief Creation Engine (DeepSeek)**: Identifies content opportunities and creates focused content briefs.
3. **Facts & Figures Acquisition Engine (Grok3)**: Gathers up-to-date factual information to enhance content quality and relevance.
4. **Content Generation Engine (Claude 3.7)**: Transforms all gathered inputs into polished, human-sounding content.
5. **Human-in-the-Loop Review System**: Enables efficient human oversight and feedback integration.

## Tech Stack

- **Agent Framework**: Agno
- **API Framework**: FastAPI
- **Deployment**: Railway.app
- **Database**: PostgreSQL
- **Language Models**: OpenAI (O3Mini), DeepSeek, Grok, Anthropic (Claude 3.7)

## Project Structure

```
seo-agent/
├── .cursor/                # Cursor IDE rules and settings
├── src/                    # Source code
│   ├── agents/             # Agent implementations
│   │   ├── research_agent.py
│   │   ├── brief_agent.py
│   │   ├── facts_agent.py
│   │   └── content_agent.py
│   ├── api/                # API endpoints and models
│   │   ├── endpoints.py
│   │   └── models.py
│   ├── config/             # Configuration settings
│   │   └── settings.py
│   ├── models/             # Data models
│   │   └── content_models.py
│   ├── services/           # Service layer
│   │   ├── llm_service.py
│   │   └── workflow_service.py
│   ├── utils/              # Utility functions
│   │   ├── error_handling.py
│   │   └── validation.py
│   ├── __init__.py
│   └── main.py             # Main application entry point
├── docs/                   # Documentation
│   ├── architecture/       # Architecture documentation
│   ├── development/        # Development guides
│   ├── features/           # Feature documentation
│   ├── systems/            # System documentation
│   └── templates/          # Documentation templates
├── tests/                  # Tests
│   ├── agents/             # Agent tests
│   ├── api/                # API tests
│   ├── services/           # Service tests
│   └── utils/              # Utility tests
├── .env.example            # Example environment variables
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose configuration
├── railway.toml            # Railway.app configuration
├── requirements.txt        # Python dependencies
└── README.md               # Project readme
```

## Setup Instructions

### Prerequisites

- Python 3.11+
- Docker and Docker Compose (optional for local development)
- API keys for OpenAI, Anthropic, DeepSeek, and Grok

### Local Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/seo-agent.git
   cd seo-agent
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   # Edit .env to add your API keys and configuration
   ```

5. Run the application:
   ```bash
   uvicorn src.main:app --reload
   ```

### Docker Setup

1. Build and start the containers:
   ```bash
   docker-compose up -d
   ```

2. Access the API at `http://localhost:8000`

### Railway.app Deployment

1. Install the Railway CLI:
   ```bash
   npm i -g @railway/cli
   ```

2. Login to Railway:
   ```bash
   railway login
   ```

3. Link to your project:
   ```bash
   railway link
   ```

4. Deploy the application:
   ```bash
   railway up
   ```

## API Documentation

Once the application is running, you can access the API documentation at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Core API Endpoints

- `GET /api/v1/health`: Check API health and model availability
- `POST /api/v1/workflows`: Create a new content generation workflow
- `GET /api/v1/workflows/{workflow_id}`: Get workflow status by ID
- `GET /api/v1/workflows`: List all workflows
- `POST /api/v1/workflows/{workflow_id}/cancel`: Cancel an active workflow
- `GET /api/v1/workflows/{workflow_id}/content`: Get generated content

## Development Workflow

1. **Setting up individual agents**:
   - Create a new agent in `src/agents/`
   - Implement Agno's Agent class interface
   - Test the agent in isolation

2. **Adding to the workflow**:
   - Update `workflow_service.py` to include the new agent
   - Define inputs and outputs between agents

3. **Testing**:
   - Unit test: `pytest tests/agents/`
   - Integration test: `pytest tests/services/`
   - API test: `pytest tests/api/`

## License

[MIT License](LICENSE)

## Contributors

- Your Name <your.email@example.com>
