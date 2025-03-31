# Contributing to SEO Agent

This guide provides instructions for developers who want to contribute to the SEO Agent project. We welcome contributions that improve the sequential pipeline, enhance agent capabilities, or add new features.

## Getting Started

Before you start contributing, please:

1. Read the [Getting Started Guide](../getting_started.md) to understand how to set up the project
2. Review the [Sequential Pipeline Architecture](../architecture/sequential-pipeline.md) to understand the system design
3. Familiarize yourself with the [development standards](#development-standards) in this document

## Development Environment

1. Fork the repository and clone your fork:
   ```bash
   git clone https://github.com/your-username/seo-agent.git
   cd seo-agent
   ```

2. Create a branch for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. Set up your development environment following the instructions in the Getting Started guide.

## Development Standards

### Code Style

- Follow PEP 8 style guidelines for Python code
- Use type hints for function parameters and return values
- Document functions, classes, and modules with docstrings
- Maintain a clean and consistent code style

### Testing

- Add tests for any new functionality
- Update existing tests when modifying functionality
- All tests should pass before submitting a pull request
- Run tests using:
  ```bash
  python -m pytest tests/
  ```

### Documentation

- Update documentation for any changes to the API or functionality
- Create new documentation for new features
- Follow the existing documentation format and style

## Contributing to the Sequential Pipeline

The sequential pipeline architecture is a core aspect of the SEO Agent. When contributing to this area, please consider the following guidelines:

### Adding a New Agent

To add a new agent to the pipeline:

1. Create a new agent implementation in `content_creation_team.py`
2. Define an appropriate system prompt for the agent
3. Select the most suitable LLM for the agent's task
4. Add the agent to the pipeline in `run_content_pipeline`
5. Update the result structure to include the new agent's output
6. Update documentation to reflect the new agent and its role

Example:

```python
# Initialize your new agent
new_agent = Agent(
    name="Your New Agent",
    system_prompt=YOUR_AGENT_SYSTEM_PROMPT,
    llm=YourSelectedLLM(model="model-name", temperature=0.7)
)

# Add to the pipeline in run_content_pipeline
def run_content_pipeline(...):
    # ... existing code ...
    
    # Run your new agent
    new_agent_output = new_agent.run(...)
    results["steps"]["your_new_agent"] = {"status": "completed", "output": new_agent_output}
    
    # ... continue with the rest of the pipeline ...
```

### Modifying Agent Configuration

When modifying an existing agent:

1. Clearly document the reason for the change
2. Test the agent with the new configuration
3. Ensure it maintains compatibility with the rest of the pipeline
4. Update system prompts in a way that maintains or improves the agent's performance

### Improving the Pipeline Flow

To improve the flow of data between agents:

1. Identify the specific improvement or issue
2. Consider how changes will affect agent interactions
3. Document the data schema for inputs and outputs
4. Test thoroughly to ensure all agents receive the data they expect

## Pull Request Process

1. Ensure your code follows the development standards
2. Update the documentation to reflect your changes
3. Add tests for your changes and ensure all tests pass
4. Push your changes to your fork and submit a pull request
5. Include a clear description of the changes and their purpose

## Review Process

Pull requests will be reviewed by the maintainers. Please be patient and responsive during the review process. We may request changes or additional information before merging your contribution.

## Adding Tests

When adding new functionality, please include appropriate tests:

### Unit Tests

Add unit tests for individual functions or classes in the `tests/unit` directory.

### Integration Tests

Add integration tests that validate the complete pipeline or significant portions of it in the `tests/integration` directory.

Example integration test structure:

```python
def test_your_feature():
    # Setup test data
    test_topic = "test topic"
    test_params = {...}
    
    # Run the pipeline or relevant parts
    results = run_content_pipeline(
        topic=test_topic,
        **test_params
    )
    
    # Assert expected outcomes
    assert "steps" in results
    assert "your_new_agent" in results["steps"]
    assert results["steps"]["your_new_agent"]["status"] == "completed"
    # Add more specific assertions related to your feature
```

## Questions and Support

If you have questions or need support, please open an issue in the repository with the label "question" or "help wanted".

Thank you for contributing to the SEO Agent project! 