#!/bin/bash
# Deploy WeatherAgent to Azure Container Instances for testing

set -e

echo "🚀 Deploying WeatherAgent to Azure Container Instances..."

# Load environment variables
source .env

# Configuration
ACR_NAME="aqr2d2acr001"
RESOURCE_GROUP="AQ-FOUNDRY-RG"
CONTAINER_NAME="weatheragent-test"
DNS_LABEL="weatheragent-test-$(date +%s)"

# Get ACR credentials
echo "🔐 Getting ACR credentials..."
ACR_USER=$(az acr credential show --name $ACR_NAME --query username -o tsv)
ACR_PASS=$(az acr credential show --name $ACR_NAME --query passwords[0].value -o tsv)

echo "📦 Creating container instance..."
az container create \
  --resource-group "$RESOURCE_GROUP" \
  --name "$CONTAINER_NAME" \
  --image "$ACR_NAME.azurecr.io/weatheragent:v2" \
  --registry-login-server "$ACR_NAME.azurecr.io" \
  --registry-username "$ACR_USER" \
  --registry-password "$ACR_PASS" \
  --dns-name-label "$DNS_LABEL" \
  --ports 8080 \
  --secure-environment-variables \
    AZURE_CLIENT_SECRET="$AZURE_CLIENT_SECRET" \
    OPENWEATHER_API_KEY="$OPENWEATHER_API_KEY" \
  --environment-variables \
    AZURE_AI_PROJECT_ENDPOINT="$AZURE_AI_PROJECT_ENDPOINT" \
    AZURE_CLIENT_ID="$AZURE_CLIENT_ID" \
    AZURE_TENANT_ID="$AZURE_TENANT_ID" \
    PORT=8080 \
    LOG_LEVEL=INFO \
  --cpu 1 \
  --memory 1 \
  --query '{FQDN:ipAddress.fqdn,IP:ipAddress.ip,State:provisioningState}' \
  -o table

# Get the FQDN
echo ""
echo "⏳ Waiting for container to start..."
sleep 10

FQDN=$(az container show --resource-group "$RESOURCE_GROUP" --name "$CONTAINER_NAME" --query ipAddress.fqdn -o tsv)

echo ""
echo "✅ Container deployed successfully!"
echo "   FQDN: $FQDN"
echo "   Health URL: http://$FQDN:8080/health"
echo ""
echo "🧪 Testing health endpoint..."
curl -s "http://$FQDN:8080/health" | python -m json.tool || echo "Container not ready yet, try again in a moment"
echo ""
echo "🧪 Test with:"
echo "   curl -X POST http://$FQDN:8080/api/messages -H 'Content-Type: application/json' -d '{\"type\":\"message\",\"from\":{\"id\":\"test\"},\"text\":\"weather in Tokyo\"}'"
