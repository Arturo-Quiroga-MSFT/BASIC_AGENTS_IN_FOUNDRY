# Hosted WeatherAgent for Agent365

This directory contains the containerized version of the WeatherAgent for deployment to Agent365 as a digital worker.

## Overview

A **hosted agent** is a containerized version of your AI agent that runs in Azure Container Instances or Azure Kubernetes Service. This enables:
- Persistent identity across Microsoft 365 applications
- Cross-application memory and state
- Enterprise-scale deployment
- Integration with Agent365 digital worker platform

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Microsoft 365                        │
│  (Teams, Outlook, Word, PowerPoint, etc.)               │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Azure Bot Service (Relay)                  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│         Agent Application (Stable Endpoint)             │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│     Hosted Agent Container (WeatherAgent)               │
│  - Activity Protocol Handler                            │
│  - Weather Function Implementation                      │
│  - State Management                                     │
│  - Authentication                                       │
└─────────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│           OpenWeatherMap API                            │
└─────────────────────────────────────────────────────────┘
```

## Files Structure

```
hosted_agent/
├── README.md                    # This file
├── Dockerfile                   # Container definition
├── requirements.txt             # Python dependencies
├── agent_server.py              # Main hosted agent server
├── activity_handler.py          # Activity Protocol handler
├── weather_functions.py         # Weather tool implementations
├── config.py                    # Configuration management
├── .dockerignore                # Docker build exclusions
├── deploy/
│   ├── build.sh                 # Build container script
│   ├── deploy.sh                # Deploy to Azure script
│   └── agent365-setup.sh        # Complete Agent365 setup
└── tests/
    └── test_agent.py            # Unit tests
```

## Prerequisites

- **Docker Desktop** installed and running
- **Azure CLI** (`az`) installed and authenticated
- **Azure Developer CLI** (`azd`) installed
- **.NET 9.0 SDK** or later
- **Azure Container Registry** access
- **Frontier Preview Program** enrollment (for Agent365)
- **Python 3.11+**

## Quick Start

### 1. Build the Container

```bash
cd hosted_agent
./deploy/build.sh
```

### 2. Test Locally

See [LOCAL_TESTING.md](LOCAL_TESTING.md) for comprehensive testing guide.

Quick test:
```bash
# Option 1: Test weather function only (no Docker, no Azure)
python test_local.py

# Option 2: Full container test with service principal
./setup-local-auth.sh  # Creates service principal and .env file
docker run -d -p 8080:8080 --env-file .env --name weatheragent-test weatheragent:latest
curl http://localhost:8080/health
```

### 3. Deploy to Azure

```bash
./deploy/deploy.sh
```

### 4. Complete Agent365 Setup

```bash
./deploy/agent365-setup.sh
```

## Environment Variables

The hosted agent requires:

```bash
# Required
OPENWEATHER_API_KEY=your_openweather_api_key
AZURE_AI_PROJECT_ENDPOINT=https://your-project.services.ai.azure.com

# Optional
PORT=8080
LOG_LEVEL=INFO
AGENT_NAME=WeatherAgent
AGENT_VERSION=2
```

## Development

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally without Docker
python agent_server.py
```

### Testing

```bash
# Run unit tests
pytest tests/

# Test with curl
curl -X POST http://localhost:8080/api/messages \
  -H "Content-Type: application/json" \
  -d '{"type": "message", "text": "What is the weather in Seattle?"}'
```

## Deployment Steps

### Step 1: Create Azure Resources

```bash
# Create Resource Group
az group create --name rg-weatheragent --location eastus

# Create Container Registry
az acr create --resource-group rg-weatheragent \
  --name weatheragentacr --sku Basic

# Create Foundry Project with hosted agent support
# (via Azure AI Foundry portal)
```

### Step 2: Build and Push Container

```bash
# Build container
docker build -t weatheragent:v2 .

# Tag for ACR
docker tag weatheragent:v2 weatheragentacr.azurecr.io/weatheragent:v2

# Login to ACR
az acr login --name weatheragentacr

# Push to ACR
docker push weatheragentacr.azurecr.io/weatheragent:v2
```

### Step 3: Register as Hosted Agent

```bash
# Register container as hosted agent in Foundry
az ai agent create-hosted \
  --project-name "Main-Project" \
  --agent-name "WeatherAgent" \
  --container-image "weatheragentacr.azurecr.io/weatheragent:v2"
```

### Step 4: Create Agent Application

```bash
# Create application with stable endpoint
az ai application create \
  --project-name "Main-Project" \
  --app-name "WeatherAgent" \
  --agent-name "WeatherAgent"
```

### Step 5: Configure Bot Service

```bash
# Create Azure Bot Service
az bot create \
  --resource-group rg-weatheragent \
  --name weatheragent-bot \
  --endpoint "https://your-app-endpoint/api/messages" \
  --msa-app-id "your-app-id"
```

### Step 6: Publish to Agent365

```bash
# Mark as digital worker and publish
az ai application publish \
  --app-name "WeatherAgent" \
  --scope "organization" \
  --digital-worker true
```

## Key Differences from Prompt Agents

| Aspect | Prompt Agent | Hosted Agent |
|--------|-------------|--------------|
| **Deployment** | Serverless | Containerized |
| **State** | Conversation-scoped | Persistent across apps |
| **Code** | Configuration-based | Full application code |
| **Scaling** | Automatic | Container orchestration |
| **Cost** | Pay per token | Container hosting + tokens |
| **Complexity** | Low | High |
| **Flexibility** | Limited to SDK | Full control |

## Benefits of Hosted Agents

✅ **Full Control**: Complete control over agent logic and behavior
✅ **Custom Infrastructure**: Run any code, use any libraries
✅ **Persistent State**: Maintain state across M365 applications
✅ **Advanced Security**: Custom authentication and authorization
✅ **Integration**: Connect to any backend system or database
✅ **Performance**: Optimize for your specific workload

## Monitoring and Logging

The hosted agent includes:
- Application Insights integration
- Structured logging
- Health check endpoints
- Metrics collection
- Distributed tracing

Access logs via:
```bash
az monitor app-insights query \
  --app your-app-insights \
  --analytics-query "traces | where message contains 'WeatherAgent'"
```

## Troubleshooting

**Container won't start:**
- Check environment variables
- Review container logs: `docker logs <container-id>`
- Verify network connectivity

**Function execution fails:**
- Verify OPENWEATHER_API_KEY is valid
- Check container has internet access
- Review application logs

**Bot Service 401 errors:**
- Verify application ID matches bot configuration
- Check RBAC permissions
- Ensure container is running and healthy

## Resources

- [Azure AI Foundry Hosted Agents](https://learn.microsoft.com/azure/ai-foundry/agents/how-to/hosted-agents)
- [Agent365 Documentation](https://learn.microsoft.com/azure/ai-foundry/agents/how-to/agent-365)
- [Activity Protocol Spec](https://learn.microsoft.com/azure/bot-service/activity-protocol)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

## Next Steps

1. ✅ Review this README
2. ⏳ Build and test container locally
3. ⏳ Deploy to Azure Container Registry
4. ⏳ Register as hosted agent in Foundry
5. ⏳ Configure Bot Service relay
6. ⏳ Publish to Agent365
7. ⏳ Test in Microsoft 365 applications

---

**Note**: Hosted agents require more infrastructure and complexity than prompt agents. Only use hosted agents when you need persistent state, custom logic, or Agent365 digital worker capabilities.
