# Dockerfile for Foundry Hosted Agent
# Based on Microsoft Foundry documentation

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8088

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY agent.py .

# Expose the port that the hosting adapter uses
EXPOSE 8088

# Health check endpoint - use /readiness which is provided by the hosting adapter
# Note: Azure Container Apps will probe /readiness automatically
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8088/readiness || exit 1

# Run the agent
CMD ["python", "-u", "agent.py"]
