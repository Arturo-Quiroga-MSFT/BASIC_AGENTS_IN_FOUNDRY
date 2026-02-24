#!/bin/bash
# Create Account-Level Capability Host for Hosted Agents
#
# This script creates the capability host required for hosted agents
# using the Azure REST API via Azure CLI.
#
# Based on Microsoft Foundry documentation:
# https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/hosted-agents

set -e

# Load configuration from .env file if it exists
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Configuration
SUBSCRIPTION_ID="${AZURE_SUBSCRIPTION_ID}"
RESOURCE_GROUP="${AZURE_RESOURCE_GROUP}"
ACCOUNT_NAME="${AZURE_FOUNDRY_ACCOUNT_NAME}"

# Validate configuration
if [ -z "$SUBSCRIPTION_ID" ]; then
    echo "❌ Error: AZURE_SUBSCRIPTION_ID is not set"
    exit 1
fi

if [ -z "$RESOURCE_GROUP" ]; then
    echo "❌ Error: AZURE_RESOURCE_GROUP is not set"
    exit 1
fi

if [ -z "$ACCOUNT_NAME" ]; then
    echo "❌ Error: AZURE_FOUNDRY_ACCOUNT_NAME is not set"
    exit 1
fi

echo "============================================================"
echo "CREATE CAPABILITY HOST"
echo "============================================================"
echo ""
echo "Configuration:"
echo "  Subscription: $SUBSCRIPTION_ID"
echo "  Resource Group: $RESOURCE_GROUP"
echo "  Account: $ACCOUNT_NAME"
echo ""

# Construct the API URL
API_URL="https://management.azure.com/subscriptions/${SUBSCRIPTION_ID}/resourceGroups/${RESOURCE_GROUP}/providers/Microsoft.CognitiveServices/accounts/${ACCOUNT_NAME}/capabilityHosts/accountcaphost?api-version=2025-10-01-preview"

# Request body
REQUEST_BODY='{
    "properties": {
        "capabilityHostKind": "Agents",
        "enablePublicHostingEnvironment": true
    }
}'

echo "Creating capability host..."
echo ""

# Make the REST API call
az rest \
    --method put \
    --url "$API_URL" \
    --headers "content-type=application/json" \
    --body "$REQUEST_BODY"

if [ $? -eq 0 ]; then
    echo ""
    echo "============================================================"
    echo "✅ Capability host created successfully!"
    echo "============================================================"
    echo ""
    echo "IMPORTANT NOTES:"
    echo "  - Capability hosts cannot be updated"
    echo "  - If you need to change settings, delete and recreate"
    echo "  - Public hosting is enabled for this capability host"
    echo ""
else
    echo ""
    echo "============================================================"
    echo "❌ Failed to create capability host"
    echo "============================================================"
    echo ""
    echo "Possible issues:"
    echo "  1. Capability host already exists"
    echo "  2. Insufficient permissions"
    echo "  3. Invalid configuration"
    echo ""
    echo "If the host exists and needs updating:"
    echo "  1. Delete it first (not covered by this script)"
    echo "  2. Then run this script again"
    echo ""
    exit 1
fi
