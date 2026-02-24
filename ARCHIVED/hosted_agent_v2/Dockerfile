FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy agent code
COPY agent.py .

# Expose both common ports.
# FoundryCBAgent defaults to 8088, but some hosted environments/probes expect 8080.
EXPOSE 8080 8088

# Add healthcheck.
# IMPORTANT: keep this aligned with the port the agent binds to.
# We honor PORT first, then DEFAULT_AD_PORT, then 8088.
HEALTHCHECK --interval=5s --timeout=3s --start-period=30s --retries=3 \
  CMD python -c "import os, urllib.request; port=os.getenv('PORT') or os.getenv('DEFAULT_AD_PORT') or '8088'; urllib.request.urlopen(f'http://localhost:{port}/readiness').read()" || exit 1

# Run the agent using the hosting adapter
CMD ["python", "agent.py"]
