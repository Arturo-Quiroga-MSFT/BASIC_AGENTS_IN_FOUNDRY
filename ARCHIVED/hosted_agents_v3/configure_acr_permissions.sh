#!/bin/bash
# Configure ACR Permissions for Foundry Project
#
# This script configures the necessary permissions for the Foundry project's
# managed identity to pull images from Azure Container Registry.
#
# Based on Microsoft Foundry documentation.

set -e

# Load configuration from .env file if it exists
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Configuration
SUBSCRIPTION_ID="${AZURE_SUBSCRIPTION_ID}"
RESOURCE_GROUP="${AZURE_RESOURCE_GROUP}"
ACCOUNT_NAME="${AZURE_FOUNDRY_ACCOUNT_NAME}"
PROJECT_NAME="${AZURE_PROJECT_NAME}"
ACR_NAME="${ACR_NAME}"

# Validate configuration
if [ -z "$SUBSCRIPTION_ID" ]; then
    echo "❌ Error: AZURE_SUBSCRIPTION_ID is not set"
    exit 1
fi

if [ -z "$RESOURCE_GROUP" ]; then
    echo "❌ Error: AZURE_RESOURCE_GROUP is not set"
    exit 1
fi

if [ -z "$PROJECT_NAME" ]; then
    echo "❌ Error: AZURE_PROJECT_NAME is not set"
    exit 1
fi

if [ -z "$ACR_NAME" ]; then
    echo "❌ Error: ACR_NAME is not set"
    exit 1
fi

echo "============================================================"
echo "CONFIGURE ACR PERMISSIONS"
echo "============================================================"
echo ""
echo "This script will:"
echo "  1. Get the Foundry project's managed identity"
echo "  2. Assign 'AcrPull' role to the managed identity"
echo ""
echo "Configuration:"
echo "  Subscription: $SUBSCRIPTION_ID"
echo "  Resource Group: $RESOURCE_GROUP"
echo "  Project: $PROJECT_NAME"
echo "  ACR: $ACR_NAME"
echo ""

# Get the project resource ID
PROJECT_RESOURCE_ID="/subscriptions/${SUBSCRIPTION_ID}/resourceGroups/${RESOURCE_GROUP}/providers/Microsoft.MachineLearningServices/workspaces/${PROJECT_NAME}"

echo "Step 1: Getting project managed identity..."
echo ""

# Get the managed identity principal ID
PRINCIPAL_ID=$(az ml workspace show \
    --name "$PROJECT_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --query identity.principalId \
    --output tsv 2>/dev/null)

if [ -z "$PRINCIPAL_ID" ]; then
    echo "❌ Could not retrieve managed identity"
    echo ""
    echo "Alternative method: Get from Azure Portal"
    echo "  1. Go to your Foundry project in Azure Portal"
    echo "  2. Navigate to: Settings → Identity"
    echo "  3. Under 'System assigned', copy the Object (principal) ID"
    echo "  4. Run the following command manually:"
    echo ""
    echo "     az role assignment create \\"
    echo "       --assignee <PRINCIPAL_ID> \\"
    echo "       --role AcrPull \\"
    echo "       --scope /subscriptions/${SUBSCRIPTION_ID}/resourceGroups/${RESOURCE_GROUP}/providers/Microsoft.ContainerRegistry/registries/${ACR_NAME}"
    echo ""
    exit 1
fi

echo "✅ Managed Identity Principal ID: $PRINCIPAL_ID"
echo ""

echo "Step 2: Assigning 'AcrPull' role..."
echo ""

# Get ACR resource ID
ACR_ID=$(az acr show \
    --name "$ACR_NAME" \
    --query id \
    --output tsv)

if [ -z "$ACR_ID" ]; then
    echo "❌ Could not find ACR: $ACR_NAME"
    exit 1
fi

echo "ACR Resource ID: $ACR_ID"
echo ""

# Assign the role
az role assignment create \
    --assignee "$PRINCIPAL_ID" \
    --role "AcrPull" \
    --scope "$ACR_ID"

if [ $? -eq 0 ]; then
    echo ""
    echo "============================================================"
    echo "✅ ACR permissions configured successfully!"
    echo "============================================================"
    echo ""
    echo "Details:"
    echo "  Principal ID: $PRINCIPAL_ID"
    echo "  Role: AcrPull"
    echo "  Scope: $ACR_ID"
    echo ""
    echo "The Foundry project can now pull images from ACR."
    echo ""
else
    echo ""
    echo "============================================================"
    echo "❌ Failed to assign role"
    echo "============================================================"
    echo ""
    echo "Possible issues:"
    echo "  1. Insufficient permissions (need User Access Administrator or Owner)"
    echo "  2. Role assignment already exists"
    echo "  3. Invalid resource IDs"
    echo ""
    exit 1
fi
