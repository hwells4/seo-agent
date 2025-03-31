# Railway Deployment Guide

This document provides instructions for deploying and maintaining the SEO Agent API on Railway.

## Prerequisites

- Railway CLI installed (`npm i -g @railway/cli`)
- Railway account and project created
- Git repository connected to Railway
- Python 3.11+ installed (as specified in Dockerfile)

## Dependencies and Installation

### Core Dependencies
The application requires specific dependencies to be installed in the following order:

1. **System Dependencies** (handled by Dockerfile):
```bash
# These are automatically installed in the Docker environment
build-essential
curl
```

2. **Base Requirements** (from requirements.txt):
```bash
pip install -r requirements.txt
```

3. **LLM Dependencies** (installed separately for version compatibility):
```bash
pip install "anthropic>=0.7.7"
pip install "openai>=1.0.0"
pip install "agno==1.2.6"
```

4. **Database Dependencies**:
```bash
pip install psycopg2-binary==2.9.9  # PostgreSQL adapter
pip install SQLAlchemy==2.0.25      # SQL ORM
```

### Dependency Groups

1. **Core Framework**:
- fastapi==0.109.2
- uvicorn==0.27.1
- pydantic==2.5.2
- python-dotenv==1.0.0

2. **Content Generation**:
- duckduckgo-search==3.9.3
- newspaper3k==0.2.8
- lxml_html_clean==0.4.1
- python-multipart==0.0.6
- requests==2.31.0

3. **Utilities**:
- tenacity==8.2.3
- tiktoken==0.5.2
- httpx

4. **Authentication**:
- python-jose==3.3.0

5. **Testing** (optional for production):
- pytest==7.4.2
- pytest-asyncio==0.21.1

### System Requirements
- Python 3.11 or higher (as specified in Dockerfile)
- Node.js 14+ (for Railway CLI)
- PostgreSQL 13+ (handled by Railway)

### Dependency Verification
After installation, you can verify key dependencies are installed correctly:
```python
# Run these commands to verify installations
python -c "import openai; print(f'OpenAI version: {openai.__version__}')"
python -c "from agno.models.openai import OpenAIChat; print('Agno OpenAI import successful')"
python -c "import anthropic; print(f'Anthropic version: {anthropic.__version__}')"
python -c "from agno.models.anthropic import Claude; print('Agno Anthropic import successful')"
```

## Initial Deployment

1. Login to Railway CLI:
```bash
railway login
```

2. Link your project:
```bash
railway link
```

3. Set up environment variables:
```bash
railway vars set OPENAI_API_KEY=your_key
railway vars set ANTHROPIC_API_KEY=your_key
# Add any other required environment variables
```

4. Deploy your project:
```bash
railway up
```

## Environment Variables

Essential environment variables that must be set:
- `OPENAI_API_KEY`: Your OpenAI API key
- `ANTHROPIC_API_KEY`: Your Anthropic API key
- `DATABASE_URL`: PostgreSQL connection string (automatically set by Railway)
- `PORT`: Server port (automatically set by Railway)

## Health Check Configuration

Railway uses the `/api/v1/health` endpoint to monitor the application's health. This endpoint should:
- Return a 200 status code
- Include basic service information
- Be responsive within the timeout period

## Troubleshooting

### Common Issues

1. **Build Failures**
   - Check build logs in Railway dashboard
   - Verify Python dependencies in requirements.txt
   - Ensure Dockerfile is properly configured

2. **Health Check Failures**
   - Verify the application is listening on the correct port
   - Check application logs for startup errors
   - Ensure environment variables are properly set

3. **Database Connection Issues**
   - Verify DATABASE_URL is properly set
   - Check database credentials
   - Ensure database migrations are up to date

### Debugging Steps

1. View logs:
```bash
railway logs
```

2. SSH into the deployment:
```bash
railway shell
```

3. Check environment variables:
```bash
railway vars
```

## Maintenance

### Updating Environment Variables
```bash
railway vars set KEY=VALUE
```

### Removing Environment Variables
```bash
railway vars unset KEY
```

### Restarting the Service
```bash
railway service restart
```

## Monitoring

- Monitor application health in Railway dashboard
- Check application logs regularly
- Set up notifications for deployment failures

## Best Practices

1. Always test locally before deploying
2. Use staging environment for testing
3. Keep environment variables updated
4. Monitor application metrics
5. Regularly update dependencies

## Rollback Procedure

If a deployment fails:
1. Access Railway dashboard
2. Navigate to Deployments
3. Find the last working deployment
4. Click "Rollback to this deployment"

## Support Resources

- [Railway Documentation](https://docs.railway.app/)
- [Railway Discord Community](https://discord.com/invite/railway)
- [Railway Status Page](https://status.railway.app/) 