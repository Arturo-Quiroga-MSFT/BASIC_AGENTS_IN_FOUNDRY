#!/bin/bash

# Deploy script for WeatherAgent v2 (FoundryCBAgent) to Azure
# This script pushes the container to Azure Container Registry

set -e

echo "🚀 Deploying WeatherAgent v2 to Azure Container Registry..."

# Configuration
ACR_NAME="${ACR_NAME:-aqr2d2acr001}"
RESOURCE_GROUP="${RESOURCE_GROUP:-AQ-FOUNDRY-RG}"
IMAGE_NAME="${IMAGE_NAME:-weatheragent}"
IMAGE_TAG="${IMAGE_TAG:-v5}"

# Check Azure CLI
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI not found. Please install: https://learn.microsoft.com/cli/azure/install-azure-cli"
    exit 1
fi

echo "📋 Configuration:"
echo "   ACR Name: ${ACR_NAME}"
echo "   Resource Group: ${RESOURCE_GROUP}"
echo "   Image: ${IMAGE_NAME}:${IMAGE_TAG}"
echo ""

# Login to Azure
echo "🔐 Checking Azure login..."
az account show &> /dev/null || az login

# Login to ACR
echo "🔐 Logging into ACR..."
az acr login --name "${ACR_NAME}"

# Get ACR login server
ACR_LOGIN_SERVER=$(az acr show --name "${ACR_NAME}" --query loginServer --output tsv)
FULL_IMAGE="${ACR_LOGIN_SERVER}/${IMAGE_NAME}:${IMAGE_TAG}"

echo "🏷️  Tagging image for ACR: ${FULL_IMAGE}"
docker tag "${IMAGE_NAME}:${IMAGE_TAG}" "${FULL_IMAGE}"

# Push to ACR
echo "📤 Pushing to Azure Container Registry..."
docker push "${FULL_IMAGE}"

if [ $? -eq 0 ]; then
    echo "✅ Deployment successful!"
    echo "   Image: ${FULL_IMAGE}"
    echo ""
    echo "Next steps:"
    echo "1. Register as hosted agent in Foundry (r2d2-hosted-agents-project, North Central US):"
    echo "   export AZURE_AI_PROJECT_ENDPOINT=https://r2d2-hosted-agents-project-resou.services.ai.azure.com/api/projects/r2d2-hosted-agents-project"
    echo "   export ACR_IMAGE=${FULL_IMAGE}"
    echo "   export AGENT_NAME=WeatherAgent6"
    echo "   python register_hosted_agent.py"
    echo ""
    echo "2. Start deployment:"
    echo "   az ai agent start --project-name r2d2-hosted-agents-project --agent-name WeatherAgent6"
else
    echo "❌ Deployment failed"
    exit 1
fi
