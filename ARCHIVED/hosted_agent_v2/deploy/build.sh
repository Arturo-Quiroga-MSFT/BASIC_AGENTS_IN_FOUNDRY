#!/bin/bash

# Build script for WeatherAgent v2 (FoundryCBAgent implementation)
# This script builds the Docker container locally

set -e

echo "🔨 Building WeatherAgent v2 hosted container (FoundryCBAgent)..."

# Configuration
IMAGE_NAME="${IMAGE_NAME:-weatheragent}"
IMAGE_TAG="${IMAGE_TAG:-v5}"
FULL_IMAGE="${IMAGE_NAME}:${IMAGE_TAG}"

# Navigate to hosted_agent_v2 directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}/.."

echo "📁 Working directory: $(pwd)"

# Build the container
echo "🐳 Building Docker image: ${FULL_IMAGE}"
docker build -t "${FULL_IMAGE}" .

# Check build success
if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    echo "   Image: ${FULL_IMAGE}"
    echo ""
    echo "To run locally:"
    echo "  docker run -p 8088:8088 \\"
    echo "    -e OPENWEATHER_API_KEY=your_key \\"
    echo "    -e AZURE_AI_PROJECT_ENDPOINT=your_endpoint \\"
    echo "    ${FULL_IMAGE}"
    echo ""
    echo "Note: FoundryCBAgent uses port 8088 (not 8080)"
else
    echo "❌ Build failed"
    exit 1
fi
