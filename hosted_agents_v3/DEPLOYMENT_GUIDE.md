# Hosted Agent Deployment Guide

Complete step-by-step guide for deploying a hosted agent in Microsoft Foundry using the Foundry SDK method.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Configuration](#configuration)
3. [Local Development & Testing](#local-development--testing)
4. [Containerization](#containerization)
5. [Azure Setup](#azure-setup)
6. [Deployment](#deployment)
7. [Testing](#testing)
8. [Management](#management)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Tools

- **Python 3.8+** installed
- **Docker** installed and running
- **Azure CLI** installed and logged in (`az login`)
- **Azure Container Registry** (ACR) set up
- **Microsoft Foundry project** created

### Required Permissions

- **Azure AI Owner** role on Foundry (if creating new project)
- **Contributor** role on Azure subscription (for ACR)
- **User Access Administrator** or **Owner** on ACR (for RBAC)
- **Reader** on Foundry account + **Azure AI User** on project (minimum)

### Region Requirements

- Hosted agents are currently available in **North Central US** only

---

## Configuration

### Step 1: Install Python Dependencies

```bash
cd hosted_agents_v3
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` with your values:

```bash
# Azure Foundry Project Configuration
AZURE_AI_PROJECT_ENDPOINT=https://your-project.services.ai.azure.com/api/projects/project-name
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_RESOURCE_GROUP=your-resource-group
AZURE_FOUNDRY_ACCOUNT_NAME=your-account-name
AZURE_PROJECT_NAME=your-project-name

# Model Configuration
MODEL_NAME=gpt-4
MODEL_DEPLOYMENT_NAME=gpt-4

# Agent Configuration
AGENT_NAME=my-hosted-agent
AGENT_VERSION=1

# Azure Container Registry
ACR_NAME=myregistry
ACR_LOGIN_SERVER=myregistry.azurecr.io
IMAGE_NAME=myagent
IMAGE_TAG=v1

# For create_agent.py - set after pushing to ACR
CONTAINER_IMAGE=myregistry.azurecr.io/myagent:v1
```

**How to find these values:**

1. **AZURE_AI_PROJECT_ENDPOINT**: 
   - Go to Azure AI Foundry portal → Your Project → Settings
   - Copy the endpoint URL

2. **AZURE_SUBSCRIPTION_ID, AZURE_RESOURCE_GROUP**:
   ```bash
   az account show --query "{subscription:id, resourceGroup:resourceGroup}"
   ```

3. **AZURE_FOUNDRY_ACCOUNT_NAME, AZURE_PROJECT_NAME**:
   - From the Azure Portal, navigate to your Foundry resources

4. **ACR_NAME, ACR_LOGIN_SERVER**:
   ```bash
   az acr list --query "[].{name:name, loginServer:loginServer}"
   ```

---

## Local Development & Testing

### Step 1: Run Agent Locally

The agent uses the hosting adapter which automatically starts an HTTP server:

```bash
python agent.py
```

Expected output:
```
Starting hosted agent...
Project Endpoint: https://your-project.services.ai.azure.com/api/projects/project-name
Model: gpt-4
Agent created: asst_xxxxx
Agent name: Simple Hosted Agent

Hosting adapter started!
Agent is now available at: http://localhost:8088
Test with: POST http://localhost:8088/responses
```

### Step 2: Test Locally with REST API

In a **new terminal**, run the test script:

```bash
# Run test suite
python test_local.py

# Run in interactive mode
python test_local.py -i
```

**Manual testing with curl:**

```bash
curl -X POST http://localhost:8088/responses \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "messages": [
        {
          "role": "user",
          "content": "Hello! What can you help me with?"
        }
      ]
    }
  }'
```

### Step 3: Verify Local Operation

✅ **Success criteria:**
- Agent starts without errors
- HTTP server responds on port 8088
- Test messages return valid responses
- No authentication errors with Azure

🛑 **If you encounter issues:**
- Check Azure credentials: `az account show`
- Verify project endpoint is correct
- Ensure model deployment exists in Foundry

---

## Containerization

### Step 1: Build Docker Image Locally

```bash
docker build -t myagent:v1 .
```

### Step 2: Test Docker Image Locally (Optional)

```bash
# Run the container
docker run -p 8088:8088 \
  -e AZURE_AI_PROJECT_ENDPOINT="your-endpoint" \
  -e MODEL_NAME="gpt-4" \
  myagent:v1

# Test in another terminal
python test_local.py
```

---

## Azure Setup

### Step 1: Login to Azure Container Registry

```bash
az acr login --name myregistry
```

### Step 2: Build and Push to ACR

Use the helper script:

```bash
./docker_build_push.sh
```

Or manually:

```bash
# Tag the image
docker tag myagent:v1 myregistry.azurecr.io/myagent:v1

# Push to ACR
docker push myregistry.azurecr.io/myagent:v1
```

### Step 3: Configure ACR Permissions

Give your Foundry project's managed identity permission to pull from ACR:

```bash
./configure_acr_permissions.sh
```

**Manual steps if script fails:**

1. Get the managed identity principal ID:
   - Azure Portal → Your Foundry Project → Identity
   - Copy the **Object (principal) ID** under System assigned

2. Assign the AcrPull role:
   ```bash
   az role assignment create \
     --assignee <PRINCIPAL_ID> \
     --role AcrPull \
     --scope /subscriptions/<SUB_ID>/resourceGroups/<RG>/providers/Microsoft.ContainerRegistry/registries/<ACR_NAME>
   ```

### Step 4: Create Account-Level Capability Host

**IMPORTANT**: This only needs to be done once per Foundry account.

```bash
./create_capability_host.sh
```

Or manually using Azure CLI:

```bash
az rest --method put \
  --url "https://management.azure.com/subscriptions/[SUBSCRIPTIONID]/resourceGroups/[RESOURCEGROUPNAME]/providers/Microsoft.CognitiveServices/accounts/[ACCOUNTNAME]/capabilityHosts/accountcaphost?api-version=2025-10-01-preview" \
  --headers "content-type=application/json" \
  --body '{
    "properties": {
      "capabilityHostKind": "Agents",
      "enablePublicHostingEnvironment": true
    }
  }'
```

**Note:** Capability hosts cannot be updated. If one exists and needs changes, delete it first, then recreate.

---

## Deployment

### Step 1: Update CONTAINER_IMAGE in .env

After pushing to ACR, update your `.env` file:

```bash
CONTAINER_IMAGE=myregistry.azurecr.io/myagent:v1
```

### Step 2: Create Hosted Agent Version

```bash
python create_agent.py
```

This script:
- Authenticates to Azure
- Creates an AI Project client
- Registers your containerized agent with Foundry
- Returns the agent version details

**Expected output:**
```
✅ Hosted agent version created successfully!

Agent Details:
  Name: my-hosted-agent
  Version: 1
  ID: agent-id-xxx

Next Steps:
1. Start the agent deployment...
```

### Step 3: Start Agent Deployment

```bash
python manage_agent.py start
```

Or with custom scaling:

```bash
python manage_agent.py start --min-replicas 1 --max-replicas 2
```

Or using Azure CLI directly:

```bash
az cognitiveservices agent start \
  --account-name <account-name> \
  --project-name <project-name> \
  --name my-hosted-agent \
  --agent-version 1
```

**Status transitions:**
- Stopped → Starting → Started (success)
- Stopped → Starting → Failed (error)

### Step 4: Monitor Deployment

Check agent status:

```bash
python manage_agent.py show
```

View container logs:

Use the REST API or Azure Portal to view logs for debugging.

---

## Testing

### Test the Deployed Agent

Once the agent is in "Started" state:

```bash
# Single test message
python invoke_agent.py

# Custom message
python invoke_agent.py "Tell me about hosted agents"

# Interactive mode
python invoke_agent.py -i
```

### Test from Azure Portal

1. Go to Azure AI Foundry portal
2. Navigate to your project
3. Go to **Agent Playground**
4. Select your hosted agent
5. Send test messages

---

## Management

### List All Agent Versions

```bash
python manage_agent.py list
```

### Update Agent Configuration

**Non-versioned update** (scaling, description):

```bash
python manage_agent.py update --min-replicas 2 --max-replicas 5
```

**Versioned update** (code, image, resources):

1. Build new image with different tag (e.g., v2)
2. Push to ACR
3. Update CONTAINER_IMAGE in .env
4. Run `python create_agent.py` (creates new version)
5. Start the new version

### Stop Agent

```bash
python manage_agent.py stop
```

### Delete Deployment (Keep Version)

```bash
python manage_agent.py delete-deployment
```

### Delete Agent Version

```bash
python manage_agent.py delete --version 1
```

### Delete All Versions

```bash
python manage_agent.py delete
```

---

## Troubleshooting

### Common Issues

#### 1. Package Version Conflicts

**Symptoms:** `ModuleNotFoundError` or import errors after installing packages

**Root Cause:** Agent Framework packages require exact version alignment:
- `azure-ai-agentserver-agentframework` must match `azure-ai-agentserver-core`
- `agent-framework` must match `agent-framework-core` exactly

**Solution:**
```bash
# If you encounter version conflicts, install compatible versions explicitly:
pip install agent-framework==1.0.0b260107 \
            agent-framework-core==1.0.0b260107 \
            agent-framework-azure-ai==1.0.0b260107 \
            azure-ai-agentserver-agentframework==1.0.0b9 \
            azure-ai-agentserver-core==1.0.0b9
```

**Prevention:** Use a fresh virtual environment with Python 3.11 or 3.12:
```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### 2. "Could not connect to the agent" (Local Testing)

**Symptoms:** Test script can't reach localhost:8088

**Solutions:**
- Verify agent.py is running
- Check if port 8088 is available: `lsof -i :8088`
- Look for errors in agent.py output
- The 404 status in health check is normal (no root endpoint exists)

#### 3. "SubscriptionIsNotRegistered" (400)

**Symptoms:** Feature or provider not registered

**Solutions:**
```bash
az provider register --namespace Microsoft.CognitiveServices
az provider register --namespace Microsoft.MachineLearningServices
```

#### 4. "InvalidAcrPullCredentials" (401)

**Symptoms:** Can't pull image from ACR

**Solutions:**
- Verify managed identity has AcrPull role
- Run `./configure_acr_permissions.sh` again
- Check ACR exists and image is pushed

#### 5. "AcrImageNotFound" (404)

**Symptoms:** Image doesn't exist in ACR

**Solutions:**
- Verify image was pushed: `az acr repository list --name <acr-name>`
- Check image name and tag match exactly
- Re-run `./docker_build_push.sh`

#### 6. Agent Deployment Fails to Start

**Symptoms:** Status stuck in "Starting" or moves to "Failed"

**Solutions:**
- View deployment logs (use Azure Portal or REST API)
- Check container logs for startup errors
- Verify environment variables are correct
- Ensure model deployment exists in Foundry

#### 7. Authentication Errors

**Symptoms:** DefaultAzureCredential fails

**Solutions:**
```bash
# Re-login to Azure
az login

# Check current account
az account show

# Set correct subscription
az account set --subscription <subscription-id>
```

#### 8. "Capability host already exists"

**Symptoms:** Can't create capability host

**Solutions:**
- This is expected if already created
- To update, must delete first (requires support)
- If exists, skip this step and proceed

### View Container Logs

Container logs help debug startup and runtime issues:

**Using REST API:**
```bash
curl -X GET \
  "https://management.azure.com/subscriptions/<SUB>/resourceGroups/<RG>/providers/Microsoft.MachineLearningServices/workspaces/<WORKSPACE>/agents/<AGENT_NAME>/versions/<VERSION>/containers/default:logstream?kind=console&tail=50" \
  -H "Authorization: Bearer $(az account get-access-token --query accessToken -o tsv)"
```

### Get Help

1. **Check agent status**: `python manage_agent.py show`
2. **View container logs**: Use Azure Portal or REST API
3. **Review documentation**: [Microsoft Foundry Hosted Agents](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/hosted-agents)
4. **Azure support**: For platform issues

---

## Next Steps

Once your hosted agent is deployed and running:

1. **Publishing**: Publish to channels (Web, Teams, M365 Copilot)
   - See: [Publish and share agents](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/publish-agent)

2. **Observability**: Set up Application Insights for tracing
   - Export OTEL traces to monitoring

3. **Tools**: Add Foundry tools (Code Interpreter, MCP, Web Search)
   - Update agent definition with tools array

4. **Evaluation**: Set up agent evaluation
   - Use Azure AI Evaluation SDK

5. **Production**: Configure scaling, monitoring, and alerts

---

## Reference Files

- `agent.py` - Main agent code with hosting adapter
- `test_local.py` - Local testing script
- `create_agent.py` - Create hosted agent version (SDK)
- `manage_agent.py` - Manage agent lifecycle (CLI)
- `invoke_agent.py` - Test deployed agent (SDK)
- `Dockerfile` - Container definition
- `docker_build_push.sh` - Build and push helper
- `configure_acr_permissions.sh` - ACR RBAC setup
- `create_capability_host.sh` - Capability host creation
- `.env` - Configuration (do not commit)
- `requirements.txt` - Python dependencies

---

## Official Documentation

- [Hosted Agents Concepts](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/hosted-agents)
- [Python Samples](https://github.com/azure-ai-foundry/foundry-samples/tree/main/samples/python/hosted-agents)
- [Azure AI Projects SDK](https://learn.microsoft.com/python/api/overview/azure/ai-projects-readme)
