#!/bin/bash
# Setup script for local testing authentication
# Creates a service principal and configures it for the weather agent

set -e

echo "🔐 Setting up local testing authentication..."
echo ""

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI is not installed. Please install it first:"
    echo "   https://learn.microsoft.com/cli/azure/install-azure-cli"
    exit 1
fi

# Check if logged in
if ! az account show &> /dev/null; then
    echo "❌ Not logged in to Azure. Please login first:"
    echo "   az login"
    exit 1
fi

# Get current subscription
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
SUBSCRIPTION_NAME=$(az account show --query name -o tsv)

echo "📋 Using subscription:"
echo "   Name: $SUBSCRIPTION_NAME"
echo "   ID: $SUBSCRIPTION_ID"
echo ""

# Prompt for resource group
read -p "Enter your Azure AI Project resource group name: " RESOURCE_GROUP

# Verify resource group exists
if ! az group show --name "$RESOURCE_GROUP" &> /dev/null; then
    echo "❌ Resource group '$RESOURCE_GROUP' not found"
    exit 1
fi

echo "✅ Resource group found"
echo ""

# Prompt for AI Project name
read -p "Enter your Azure AI Project name: " PROJECT_NAME

# Get project resource ID
PROJECT_RESOURCE_ID=$(az cognitiveservices account show \
    --name "$PROJECT_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --query id -o tsv 2>/dev/null || echo "")

if [ -z "$PROJECT_RESOURCE_ID" ]; then
    echo "❌ AI Project '$PROJECT_NAME' not found in resource group '$RESOURCE_GROUP'"
    exit 1
fi

echo "✅ AI Project found: $PROJECT_RESOURCE_ID"
echo ""

# Create service principal
echo "🔨 Creating service principal..."
SP_NAME="weather-agent-local-test-$(date +%s)"

SP_OUTPUT=$(az ad sp create-for-rbac \
    --name "$SP_NAME" \
    --role "Cognitive Services User" \
    --scopes "$PROJECT_RESOURCE_ID" \
    --query '{clientId:appId, clientSecret:password, tenantId:tenant}' \
    -o json)

CLIENT_ID=$(echo "$SP_OUTPUT" | jq -r '.clientId')
CLIENT_SECRET=$(echo "$SP_OUTPUT" | jq -r '.clientSecret')
TENANT_ID=$(echo "$SP_OUTPUT" | jq -r '.tenantId')

echo "✅ Service principal created: $SP_NAME"
echo ""

# Get AI Project endpoint
PROJECT_ENDPOINT=$(az cognitiveservices account show \
    --name "$PROJECT_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --query "properties.endpoint" -o tsv)

echo "📝 Configuration values:"
echo ""
echo "AZURE_CLIENT_ID=$CLIENT_ID"
echo "AZURE_CLIENT_SECRET=$CLIENT_SECRET"
echo "AZURE_TENANT_ID=$TENANT_ID"
echo "AZURE_AI_PROJECT_ENDPOINT=$PROJECT_ENDPOINT"
echo ""

# Prompt for OpenWeather API key
read -p "Enter your OpenWeatherMap API key (or press Enter to skip): " OPENWEATHER_KEY
echo ""

# Update .env file
if [ -f ".env" ]; then
    echo "⚠️  .env file already exists. Creating backup..."
    cp .env .env.backup
    echo "✅ Backup created: .env.backup"
fi

echo "📄 Writing .env file..."

cat > .env <<EOF
# Azure AI Project Configuration
AZURE_AI_PROJECT_ENDPOINT=$PROJECT_ENDPOINT

# Service Principal Authentication (for local Docker testing)
AZURE_CLIENT_ID=$CLIENT_ID
AZURE_CLIENT_SECRET=$CLIENT_SECRET
AZURE_TENANT_ID=$TENANT_ID

# OpenWeather API Key
OPENWEATHER_API_KEY=${OPENWEATHER_KEY:-your_api_key_here}

# Agent Configuration
PORT=8080
LOG_LEVEL=INFO
AGENT_NAME=WeatherAgent
AGENT_VERSION=2
EOF

echo "✅ .env file created"
echo ""

echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. If you skipped it, add your OpenWeather API key to .env"
echo "   2. Build the container: ./deploy/build.sh"
echo "   3. Run the container: docker run -d -p 8080:8080 --env-file .env --name weatheragent-test weatheragent:latest"
echo "   4. Test: curl http://localhost:8080/health"
echo ""
echo "⚠️  IMPORTANT: Save these credentials securely!"
echo "   Client ID: $CLIENT_ID"
echo "   Client Secret: $CLIENT_SECRET"
echo "   (These are also in your .env file)"
echo ""
echo "🗑️  To cleanup later:"
echo "   az ad sp delete --id $CLIENT_ID"
