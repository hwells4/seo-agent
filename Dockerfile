# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python packages in the correct order
RUN pip install --upgrade pip && \
    pip install --no-cache-dir "anthropic>=0.7.7" && \
    pip install --no-cache-dir "openai>=1.0.0" && \
    pip install --no-cache-dir "agno==1.2.6" && \
    pip install --no-cache-dir -r requirements.txt

# Verify installations
RUN python -c "import openai; print(f'OpenAI version: {openai.__version__}')" && \
    python -c "from agno.models.openai import OpenAIChat; print('Agno OpenAI import successful')" && \
    python -c "import anthropic; print(f'Anthropic version: {anthropic.__version__}')" && \
    python -c "from agno.models.anthropic import Claude; print('Agno Anthropic import successful')"

# Copy the rest of the application
COPY . .

# Set environment variables
ENV PYTHONPATH=/app \
    PORT=8000

# Create a startup script
RUN echo '#!/bin/sh\n\
PORT="${PORT:-8000}"\n\
echo "Starting server on port $PORT..."\n\
exec uvicorn api.base:app --host 0.0.0.0 --port "$PORT"' > /start.sh && \
    chmod +x /start.sh

# Start the application using the startup script
CMD ["/start.sh"]
