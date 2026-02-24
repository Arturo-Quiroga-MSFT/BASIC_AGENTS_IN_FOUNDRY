#!/bin/bash

# Complete Agent365 setup script
# This script performs all steps to publish WeatherAgent to Agent365

set -e

echo "🎯 Complete Agent365 Setup for WeatherAgent"
echo "==========================================="
echo ""

# Configuration
PROJECT_NAME="${PROJECT_NAME:-Main-Project}"
AGENT_NAME="${AGENT_NAME:-WeatherAgent}"
ACR_NAME="${ACR_NAME:-weatheragentacr}"
IMAGE_NAME="${IMAGE_NAME:-weatheragent}"
IMAGE_TAG="${IMAGE_TAG:-v2}"
BOT_NAME="${BOT_NAME:-weatheragent-bot}"
RESOURCE_GROUP="${RESOURCE_GROUP:-rg-weatheragent}"

echo "📋 Configuration:"
echo "   Project: ${PROJECT_NAME}"
echo "   Agent: ${AGENT_NAME}"
echo "   ACR: ${ACR_NAME}"
echo "   Image: ${IMAGE_NAME}:${IMAGE_TAG}"
echo "   Bot: ${BOT_NAME}"
echo ""

# Ensure logged in
echo "🔐 Checking Azure login..."
az account show &> /dev/null || az login

# Get ACR login server
ACR_LOGIN_SERVER=$(az acr show --name "${ACR_NAME}" --query loginServer --output tsv)
FULL_IMAGE="${ACR_LOGIN_SERVER}/${IMAGE_NAME}:${IMAGE_TAG}"

echo "📸 Container image: ${FULL_IMAGE}"
echo ""

# Step 1: Register as hosted agent
echo "Step 1: Register as hosted agent in Foundry"
echo "-------------------------------------------"
echo "⚠️  This step requires Azure AI Foundry CLI or portal"
echo ""
echo "Via Portal:"
echo "  1. Go to https://ai.azure.com"
echo "  2. Navigate to your project: ${PROJECT_NAME}"
echo "  3. Go to 'Agents' → 'Create' → 'Hosted Agent'"
echo "  4. Enter:"
echo "     - Name: ${AGENT_NAME}"
echo "     - Container Image: ${FULL_IMAGE}"
echo "     - Port: 8080"
echo "     - Health Endpoint: /health"
echo ""
read -p "Press Enter once hosted agent is created..."

# Step 2: Create Agent Application
echo ""
echo "Step 2: Create Agent Application"
echo "--------------------------------"
echo "⚠️  This step requires Azure AI Foundry portal"
echo ""
echo "Via Portal:"
echo "  1. Select your hosted agent: ${AGENT_NAME}"
echo "  2. Click 'Publish' → 'Create Agent Application'"
echo "  3. Configure:"
echo "     - Name: ${AGENT_NAME}"
echo "     - Description: Weather agent for Agent365"
echo "     - Enable Bot Service integration"
echo ""
read -p "Press Enter once application is created..."

# Step 3: Get Application Endpoint
echo ""
echo "Step 3: Get Application Endpoint"
echo "--------------------------------"
read -p "Enter the Application Endpoint URL: " APP_ENDPOINT

# Step 4: Create Azure Bot Service
echo ""
echo "Step 4: Create Azure Bot Service"
echo "--------------------------------"
echo "Creating Bot Service: ${BOT_NAME}"

# Note: This would require Microsoft App ID/Password
echo "⚠️  Bot Service creation requires additional authentication setup"
echo ""
echo "To create manually:"
echo "  1. Go to Azure Portal"
echo "  2. Create 'Azure Bot' resource"
echo "  3. Configure:"
echo "     - Bot handle: ${BOT_NAME}"
echo "     - Messaging endpoint: ${APP_ENDPOINT}/api/messages"
echo "     - Microsoft App ID: (use Application's identity)"
echo "  4. Enable channels: Microsoft Teams, M365 Extensions"
echo ""
read -p "Press Enter once Bot Service is created..."

# Step 5: Publish to Agent365
echo ""
echo "Step 5: Publish to Agent365"
echo "---------------------------"
echo "⚠️  This step requires Azure AI Foundry portal"
echo ""
echo "Via Portal:"
echo "  1. Go to your Agent Application: ${AGENT_NAME}"
echo "  2. Click 'Publish to Microsoft 365'"
echo "  3. Fill in metadata:"
echo "     - Display Name: ${AGENT_NAME}"
echo "     - Description: Real-time weather information assistant"
echo "     - Category: Productivity"
echo "     - Publisher: Your Organization"
echo "  4. Mark as 'Digital Worker': Yes"
echo "  5. Select publish scope: Organization"
echo "  6. Submit for approval"
echo ""
read -p "Press Enter once published..."

# Step 6: Admin Approval
echo ""
echo "Step 6: Admin Approval Required"
echo "-------------------------------"
echo "📧 Notify your Microsoft 365 admin to approve the agent in:"
echo "   Microsoft 365 Admin Center → Settings → Integrated apps"
echo ""
echo "Once approved, the agent will appear in Agent365 for all users!"

echo ""
echo "✅ Setup complete!"
echo ""
echo "📚 Documentation:"
echo "   - Azure AI Foundry: https://ai.azure.com"
echo "   - Agent365 Docs: https://learn.microsoft.com/azure/ai-foundry/agents/how-to/agent-365"
echo ""
echo "🎉 Your WeatherAgent is now ready for Agent365!"
