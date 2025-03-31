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
PORT="${PORT:-8000}"\n\
nc -zv localhost $PORT || exit 1\n\
curl -f http://localhost:$PORT/api/v1/health || exit 1' > /healthcheck.sh && \
    chmod +x /healthcheck.sh

# Expose the port
EXPOSE 8000

# Health check using netcat and curl
HEALTHCHECK --interval=5s --timeout=3s --start-period=5s --retries=3 \
    CMD /healthcheck.sh

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
python3 -m uvicorn api.base:app --host 0.0.0.0 --port $PORT --log-level debug' > /start.sh && \
    chmod +x /start.sh

# Set the PYTHONPATH
ENV PYTHONPATH=/app

# Run the startup script
CMD ["/start.sh"]
