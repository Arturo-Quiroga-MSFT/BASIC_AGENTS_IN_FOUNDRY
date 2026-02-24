#!/bin/bash
# Docker Build and Push Helper Script
#
# This script helps build and push the hosted agent Docker image to ACR.
# Based on Microsoft Foundry documentation.

set -e

# Load configuration from .env file if it exists
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Configuration
ACR_NAME="${ACR_NAME}"
ACR_LOGIN_SERVER="${ACR_LOGIN_SERVER}"
IMAGE_NAME="${IMAGE_NAME:-myagent}"
IMAGE_TAG="${IMAGE_TAG:-v1}"

# Validate configuration
if [ -z "$ACR_NAME" ]; then
    echo "❌ Error: ACR_NAME is not set"
    exit 1
fi

if [ -z "$ACR_LOGIN_SERVER" ]; then
    echo "❌ Error: ACR_LOGIN_SERVER is not set"
    exit 1
fi

echo "============================================================"
echo "DOCKER BUILD AND PUSH"
echo "============================================================"
echo ""
echo "Configuration:"
echo "  ACR Name: $ACR_NAME"
echo "  ACR Server: $ACR_LOGIN_SERVER"
echo "  Image Name: $IMAGE_NAME"
echo "  Image Tag: $IMAGE_TAG"
echo ""

# Full image name for local build
LOCAL_IMAGE="${IMAGE_NAME}:${IMAGE_TAG}"

# Full image name for ACR
ACR_IMAGE="${ACR_LOGIN_SERVER}/${IMAGE_NAME}:${IMAGE_TAG}"

echo "============================================================"
echo "STEP 1: Build Docker Image"
echo "============================================================"
echo ""
echo "Building: $LOCAL_IMAGE"
echo ""

docker build -t "$LOCAL_IMAGE" .

if [ $? -ne 0 ]; then
    echo "❌ Docker build failed"
    exit 1
fi

echo ""
echo "✅ Build successful!"
echo ""

echo "============================================================"
echo "STEP 2: Login to Azure Container Registry"
echo "============================================================"
echo ""

az acr login --name "$ACR_NAME"

if [ $? -ne 0 ]; then
    echo "❌ ACR login failed"
    exit 1
fi

echo ""
echo "✅ ACR login successful!"
echo ""

echo "============================================================"
echo "STEP 3: Tag Image for ACR"
echo "============================================================"
echo ""
echo "Tagging: $LOCAL_IMAGE → $ACR_IMAGE"
echo ""

docker tag "$LOCAL_IMAGE" "$ACR_IMAGE"

if [ $? -ne 0 ]; then
    echo "❌ Docker tag failed"
    exit 1
fi

echo "✅ Tag successful!"
echo ""

echo "============================================================"
echo "STEP 4: Push Image to ACR"
echo "============================================================"
echo ""
echo "Pushing: $ACR_IMAGE"
echo ""

docker push "$ACR_IMAGE"

if [ $? -ne 0 ]; then
    echo "❌ Docker push failed"
    exit 1
fi

echo ""
echo "============================================================"
echo "✅ SUCCESS! Image pushed to ACR"
echo "============================================================"
echo ""
echo "Image details:"
echo "  Full image name: $ACR_IMAGE"
echo ""
echo "Next steps:"
echo "  1. Configure ACR permissions (see configure_acr_permissions.sh)"
echo "  2. Create capability host (see create_capability_host.sh)"
echo "  3. Create hosted agent version:"
echo "     Update CONTAINER_IMAGE in .env to: $ACR_IMAGE"
echo "     Then run: python create_agent.py"
echo ""
