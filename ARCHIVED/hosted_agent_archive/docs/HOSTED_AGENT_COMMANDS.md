# Hosted Agent CLI Commands Reference

This document captures all working Azure CLI commands used for deploying and managing the WeatherAgent as a hosted agent in Azure AI Foundry.

## Prerequisites

```bash
# Ensure you're logged into Azure
az login

# Set the correct subscription (if needed)
az account set --subscription "your-subscription-id"
```

---

## 1. Container Registry Commands

### Build and Push Docker Image

```bash
# Navigate to the hosted_agent directory
cd /Users/arturoquiroga/GITHUB/BASIC_AGENTS_IN_FOUNDRY/hosted_agent

# Build the Docker image
docker build -t weatheragent:v2 -f deploy/Dockerfile .

# Tag for Azure Container Registry
docker tag weatheragent:v2 aqr2d2acr001.azurecr.io/weatheragent:v2

# Login to ACR
az acr login --name aqr2d2acr001

# Push to ACR
docker push aqr2d2acr001.azurecr.io/weatheragent:v2
```

### Verify Image in ACR

```bash
# List repositories in ACR
az acr repository list --name aqr2d2acr001 -o table

# Show tags for the weatheragent repository
az acr repository show-tags --name aqr2d2acr001 --repository weatheragent -o table
```

---

## 2. Capability Host Commands

Capability hosts are required infrastructure for hosted agents in Azure AI Foundry.

### Check Capability Host Status

```bash
# Get capability host details via REST API
curl -s -X GET \
  "https://management.azure.com/subscriptions/28ab7f60-4feb-4146-8a72-7ca378aac299/resourceGroups/AQ-FOUNDRY-RG/providers/Microsoft.CognitiveServices/accounts/r2d2-hosted-agents-project-resou/capabilityHosts/default?api-version=2025-04-01-preview" \
  -H "Authorization: Bearer $(az account get-access-token --query accessToken -o tsv)" \
  -H "Content-Type: application/json" | jq .
```

### Create Capability Host (if not exists)

```bash
# Create capability host via REST API
curl -s -X PUT \
  "https://management.azure.com/subscriptions/28ab7f60-4feb-4146-8a72-7ca378aac299/resourceGroups/AQ-FOUNDRY-RG/providers/Microsoft.CognitiveServices/accounts/r2d2-hosted-agents-project-resou/capabilityHosts/default?api-version=2025-04-01-preview" \
  -H "Authorization: Bearer $(az account get-access-token --query accessToken -o tsv)" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "capabilityHostKind": "Agents"
    }
  }' | jq .
```

**Expected Response:**
```json
{
  "properties": {
    "capabilityHostKind": "Agents",
    "provisioningState": "Succeeded"
  }
}
```

---

## 3. Hosted Agent Management Commands

### List All Agents in Project

```bash
az cognitiveservices agent list \
  --account-name r2d2-hosted-agents-project-resou \
  --project-name r2d2-hosted-agents-project \
  -o table
```

### Show Agent Details

```bash
az cognitiveservices agent show \
  --account-name r2d2-hosted-agents-project-resou \
  --project-name r2d2-hosted-agents-project \
  --name WeatherAgent \
  -o json
```

**Output includes:** Agent name, versions, container image, environment variables, CPU/memory allocation.

### List Agent Versions

```bash
az cognitiveservices agent list-versions \
  --account-name r2d2-hosted-agents-project-resou \
  --project-name r2d2-hosted-agents-project \
  --name WeatherAgent \
  -o json
```

### Get Specific Version Details

```bash
az cognitiveservices agent list-versions \
  --account-name r2d2-hosted-agents-project-resou \
  --project-name r2d2-hosted-agents-project \
  --name WeatherAgent \
  -o json 2>/dev/null | jq '.[0]'
```

---

## 4. Agent Lifecycle Commands

### Start a Hosted Agent

```bash
az cognitiveservices agent start \
  --account-name r2d2-hosted-agents-project-resou \
  --project-name r2d2-hosted-agents-project \
  --name WeatherAgent \
  --agent-version 1 \
  -o json
```

**Response includes:**
- `status`: Overall operation status ("InProgress", "Succeeded")
- `container.status`: Container state ("Starting", "Running", "Stopped")
- `container.error_message`: Any errors during startup

### Check Agent Start Status (Quick View)

```bash
az cognitiveservices agent start \
  --account-name r2d2-hosted-agents-project-resou \
  --project-name r2d2-hosted-agents-project \
  --name WeatherAgent \
  --agent-version 1 \
  -o json 2>&1 | jq '{status: .status, container_status: .container.status}'
```

### Stop a Hosted Agent

```bash
az cognitiveservices agent stop \
  --account-name r2d2-hosted-agents-project-resou \
  --project-name r2d2-hosted-agents-project \
  --name WeatherAgent \
  --agent-version 1 \
  -o json
```

---

## 5. Agent Registration (SDK)

For registering new agent versions programmatically, use the Python SDK:

```python
# See register_hosted_agent.py for full implementation
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import ImageBasedHostedAgentDefinition

client = AIProjectClient(endpoint=PROJECT_ENDPOINT, credential=credential)

definition = ImageBasedHostedAgentDefinition(
    image="aqr2d2acr001.azurecr.io/weatheragent:v2",
    cpu="1",
    memory="2Gi",
    environment_variables={
        "OPENWEATHER_API_KEY": "your-api-key",
        "PORT": "8080",
        # ...
    }
)

agent_version = client.agents.create_hosted_agent_version(
    name="WeatherAgent",
    version="1",
    description="Weather agent (hosted)",
    definition=definition
)
```

---

## 6. Local Testing Commands

### Test Container Locally with Docker

```bash
# Run container locally (requires service principal credentials)
docker run --rm -p 8080:8080 \
  --env-file .env \
  -e AZURE_CLIENT_ID="your-sp-client-id" \
  -e AZURE_CLIENT_SECRET="your-sp-secret" \
  -e AZURE_TENANT_ID="your-tenant-id" \
  aqr2d2acr001.azurecr.io/weatheragent:v2
```

### Send Test Request via Activity Protocol

```bash
curl -X POST http://localhost:8080/activities \
  -H "Content-Type: application/json" \
  -d '{
    "type": "message",
    "id": "test-001",
    "from": {"id": "user", "name": "User"},
    "conversation": {"id": "conv-001"},
    "text": "What is the weather in Mexico City?"
  }'
```

---

## 7. Useful Diagnostic Commands

### Get Azure Access Token

```bash
az account get-access-token --query accessToken -o tsv
```

### Check Current Azure Account

```bash
az account show -o table
```

### List Resource Groups

```bash
az group list -o table
```

### List Cognitive Services Accounts

```bash
az cognitiveservices account list -g AQ-FOUNDRY-RG -o table
```

---

## Configuration Reference

| Parameter | Value |
|-----------|-------|
| **Account Name** | `r2d2-hosted-agents-project-resou` |
| **Project Name** | `r2d2-hosted-agents-project` |
| **Resource Group** | `AQ-FOUNDRY-RG` |
| **Region** | North Central US |
| **Container Registry** | `aqr2d2acr001.azurecr.io` |
| **Container Image** | `aqr2d2acr001.azurecr.io/weatheragent:v2` |
| **Agent Name** | `WeatherAgent` |
| **Agent Version** | `1` |
| **Project Endpoint** | `https://r2d2-hosted-agents-project-resou.services.ai.azure.com/api/projects/r2d2-hosted-agents-project` |

---

## Status Values Reference

### Agent Start Status
- `InProgress` - Deployment in progress
- `Succeeded` - Successfully started
- `Failed` - Deployment failed

### Container Status
- `Starting` - Container is initializing (1-5 minutes typical)
- `Running` - Container is active and ready
- `Stopped` - Container has been stopped
- `Failed` - Container failed to start (check `error_message`)

---

## Troubleshooting

### Agent stuck in "Starting"
1. Wait 3-5 minutes for container pull and initialization
2. Check container logs in Azure Portal
3. Verify ACR image is accessible
4. Ensure capability host is provisioned

### "Capability host not found"
Run the capability host creation command (section 2).

### 404 errors on agent commands
Verify:
- Account name and project name are correct
- Hosted agents are supported in your region (North Central US required)
- You have the correct permissions

---

## Portal Links

- **Azure AI Foundry Portal**: https://ai.azure.com
- **Project URL**: https://ai.azure.com/nextgen/r/eiyHg0-RDWmhtkoidTuIg,AQ-FOUNDRY-RG,,r2d2-hosted-agents-project-resou,r2d2-hosted-agents-project/Build/agents
