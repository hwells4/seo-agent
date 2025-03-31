# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir "openai>=1.0.0,<2.0.0" && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0
ENV PORT=8000
ENV LOG_LEVEL=debug

# Create a health check script
RUN echo '#!/bin/sh\n\
nc -zv localhost 8000 || exit 1\n\
curl -f http://localhost:8000/api/v1/health || exit 1' > /healthcheck.sh && \
    chmod +x /healthcheck.sh

# Expose the port
EXPOSE 8000

# Health check using netcat and curl
HEALTHCHECK --interval=5s --timeout=3s --start-period=5s --retries=3 \
    CMD /healthcheck.sh

# Create startup script with environment variable check
RUN echo '#!/bin/sh\n\
echo "Starting server on port 8000..."\n\
echo "Checking environment variables..."\n\
if [ -z "$OPENAI_API_KEY" ]; then echo "Warning: OPENAI_API_KEY not set"; fi\n\
if [ -z "$ANTHROPIC_API_KEY" ]; then echo "Warning: ANTHROPIC_API_KEY not set"; fi\n\
if [ -z "$DEEPSEEK_API_KEY" ]; then echo "Warning: DEEPSEEK_API_KEY not set"; fi\n\
if [ -z "$XAI_API_KEY" ]; then echo "Warning: XAI_API_KEY not set"; fi\n\
python3 -m uvicorn minimal_server:app --host 0.0.0.0 --port 8000 --log-level debug' > /start.sh && \
    chmod +x /start.sh

# Run the server
CMD ["/start.sh"]
