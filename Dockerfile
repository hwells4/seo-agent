# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    netcat-traditional \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0
ENV PORT=8000
ENV LOG_LEVEL=debug

# Create a health check script
RUN echo '#!/bin/sh\n\
sleep 10\n\
PORT="${PORT:-8000}"\n\
for i in 1 2 3; do\n\
    echo "Health check attempt $i..."\n\
    if nc -z localhost $PORT && curl -f http://localhost:$PORT/api/v1/health; then\n\
        echo "Health check passed!"\n\
        exit 0\n\
    fi\n\
    sleep 5\n\
done\n\
echo "Health check failed after 3 attempts"\n\
exit 1' > /healthcheck.sh && \
    chmod +x /healthcheck.sh

# Expose the port
EXPOSE 8000

# Health check using netcat and curl
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 CMD /healthcheck.sh

# Create startup script with environment variable check
RUN echo '#!/bin/sh\n\
echo "Starting server..."\n\
echo "Checking environment variables..."\n\
if [ -z "$OPENAI_API_KEY" ]; then echo "Warning: OPENAI_API_KEY not set"; fi\n\
if [ -z "$ANTHROPIC_API_KEY" ]; then echo "Warning: ANTHROPIC_API_KEY not set"; fi\n\
if [ -z "$DEEPSEEK_API_KEY" ]; then echo "Warning: DEEPSEEK_API_KEY not set"; fi\n\
if [ -z "$XAI_API_KEY" ]; then echo "Warning: XAI_API_KEY not set"; fi\n\
PORT="${PORT:-8000}"\n\
echo "Using port: $PORT"\n\
echo "Starting FastAPI application..."\n\
exec python3 -m uvicorn api.base:app --host 0.0.0.0 --port $PORT --log-level debug' > /start.sh && \
    chmod +x /start.sh

# Set the PYTHONPATH
ENV PYTHONPATH=/app

# Run the startup script
CMD ["/start.sh"]
