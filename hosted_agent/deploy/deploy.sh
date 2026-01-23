#!/bin/bash

# Deploy script for WeatherAgent hosted container to Azure
# This script pushes the container to Azure Container Registry

set -e

echo "🚀 Deploying WeatherAgent to Azure Container Registry..."

# Configuration
ACR_NAME="${ACR_NAME:-weatheragentacr}"
RESOURCE_GROUP="${RESOURCE_GROUP:-rg-weatheragent}"
LOCATION="${LOCATION:-eastus}"
IMAGE_NAME="${IMAGE_NAME:-weatheragent}"
IMAGE_TAG="${IMAGE_TAG:-v2}"

# Check Azure CLI
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI not found. Please install: https://learn.microsoft.com/cli/azure/install-azure-cli"
    exit 1
fi

echo "📋 Configuration:"
echo "   ACR Name: ${ACR_NAME}"
echo "   Resource Group: ${RESOURCE_GROUP}"
echo "   Location: ${LOCATION}"
echo "   Image: ${IMAGE_NAME}:${IMAGE_TAG}"
echo ""

# Login to Azure
echo "🔐 Checking Azure login..."
az account show &> /dev/null || az login

# Create resource group if it doesn't exist
echo "📦 Creating resource group..."
az group create --name "${RESOURCE_GROUP}" --location "${LOCATION}" --output none || true

# Create ACR if it doesn't exist
echo "🗄️  Creating Azure Container Registry..."
az acr create \
    --resource-group "${RESOURCE_GROUP}" \
    --name "${ACR_NAME}" \
    --sku Basic \
    --output none || true

# Login to ACR
echo "🔐 Logging into ACR..."
az acr login --name "${ACR_NAME}"

# Get ACR login server
ACR_LOGIN_SERVER=$(az acr show --name "${ACR_NAME}" --query loginServer --output tsv)
FULL_IMAGE="${ACR_LOGIN_SERVER}/${IMAGE_NAME}:${IMAGE_TAG}"

echo "🏷️  Tagging image for ACR: ${FULL_IMAGE}"
docker tag "${IMAGE_NAME}:latest" "${FULL_IMAGE}"

# Push to ACR
echo "📤 Pushing to Azure Container Registry..."
docker push "${FULL_IMAGE}"

if [ $? -eq 0 ]; then
    echo "✅ Deployment successful!"
    echo "   Image: ${FULL_IMAGE}"
    echo ""
    echo "Next steps:"
    echo "1. Register as hosted agent in Azure AI Foundry"
    echo "2. Create agent application"
    echo "3. Configure Bot Service"
    echo "4. Publish to Agent365"
else
    echo "❌ Deployment failed"
    exit 1
fi
