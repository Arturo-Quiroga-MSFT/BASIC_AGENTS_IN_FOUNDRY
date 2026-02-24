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

### Common Issues and Solutions

#### Container won't start:
- Check environment variables
- Review container logs: `docker logs <container-id>`
- Verify network connectivity

#### Function execution fails:
- Verify OPENWEATHER_API_KEY is valid
- Check container has internet access
- Review application logs

#### Bot Service 401 errors:
- Verify application ID matches bot configuration
- Check RBAC permissions
- Ensure container is running and healthy

---

## Implementation Journey: Custom vs Official SDK

### Initial Approach - Custom aiohttp Server (Failed in Azure)

**What We Built:**
- Custom aiohttp server implementing Activity Protocol and Responses API
- Manual endpoint handling for `/responses`, `/api/messages`, `/health`
- Custom activity handler with message parsing
- Files: `agent_server.py`, `activity_handler.py`

**Local Testing: ✅ SUCCESS**
- Container started in 5 seconds
- All endpoints functional
- Weather queries working perfectly
- Health checks passing

**Azure Deployment: ❌ FAILED**
- All deployments stuck in "Starting" status indefinitely (10+ minutes)
- No clear error messages in portal
- Multiple attempts with different configurations all failed:
  - WeatherAgent through WeatherAgent5
  - Different image versions (v2, v3, v4)
  - Various endpoint configurations
  - ACR permission fixes (AcrPull granted to both identities)

**Key Findings:**
- Custom server implementation works locally but Azure environment requires specific patterns
- Preview service may have undocumented requirements
- Official SDK provides necessary integration layer

### Final Solution - Azure AI Agent Server Core (SUCCESS)

**Migration to Official Pattern:**
Switched to `azure-ai-agentserver-core` package with `FoundryCBAgent` class following Microsoft's official pattern from documentation.

**New Implementation (hosted_agent_v2/):**
```python
from azure.ai.agentserver.core import FoundryCBAgent

async def agent_run(request_body):
    # Extract message from AgentRunContext
    user_message = ""
    if hasattr(request_body, 'request') and isinstance(request_body.request, dict):
        messages = request_body.request.get('messages', [])
        for msg in messages:
            if isinstance(msg, dict) and msg.get('role') == 'user':
                user_message = msg.get('content', '')
                break
    
    # Process weather query
    # Return OpenAIResponse or stream events

my_agent = FoundryCBAgent()
my_agent.agent_run = agent_run
my_agent.run()  # Runs on localhost:8088
```

**Critical Differences:**
1. **Request Structure**: Custom server received raw HTTP requests; FoundryCBAgent provides `AgentRunContext` wrapper
2. **Message Extraction**: Context has `request` property containing dict with `messages` array
3. **Environment Loading**: Must explicitly call `load_dotenv()` before imports
4. **Protocol Translation**: SDK handles Activity Protocol ↔ Responses API conversion automatically
5. **OpenTelemetry**: Built-in tracing and diagnostics
6. **Port**: Default 8088 (not 8080)

**Troubleshooting Steps That Led to Success:**

1. **Empty User Messages Issue:**
   - **Problem**: `user_message` always empty despite correct curl payload
   - **Debug**: Added logging to inspect `request_body` attributes
   - **Root Cause**: Tried accessing non-existent `messages` attribute directly
   - **Solution**: Access via `request_body.request` (dict) then extract from `messages` array

2. **Weather API Key Not Found:**
   - **Problem**: `os.getenv("OPENWEATHER_API_KEY")` returned None
   - **Root Cause**: `.env` file existed but never loaded
   - **Solution**: Added `from dotenv import load_dotenv` and `load_dotenv()` at module level

3. **Request Context Understanding:**
   - **Problem**: Confusion about data structure
   - **Discovery Process**:
     ```python
     # Added debug logging:
     logger.info(f"Request dir: {dir(request_body)}")
     # Found: 'request', 'raw_payload', 'stream', 'response_id', etc.
     
     logger.info(f"Request object: {request_body.request}")
     # Revealed: {'messages': [{'role': 'user', 'content': '...'}], 'model': '...', 'stream': False}
     ```
   - **Key Insight**: `AgentRunContext` wraps the actual request dict in the `request` property

**Files for Official Implementation:**
- `hosted_agent_v2/agent.py` - FoundryCBAgent with agent_run handler
- `hosted_agent_v2/requirements.txt` - azure-ai-agentserver-core==1.0.0b8
- `hosted_agent_v2/Dockerfile` - Standard Python 3.11-slim with port 8088
- `hosted_agent_v2/.env` - Must include OPENWEATHER_API_KEY (loaded via dotenv)

**Local Testing Success:**
```bash
# Terminal 1: Run agent
cd hosted_agent_v2
source ../.venv/bin/activate
python agent.py
# INFO: Uvicorn running on http://0.0.0.0:8088

# Terminal 2: Test with curl
curl -X POST http://localhost:8088/responses \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"What is the weather in Mexico City?"}],"model":"weather-agent","stream":false}'

# Response:
{"metadata":{},"temperature":0.0,"top_p":0.0,"user":"user","id":"resp_...","created_at":...,"output":[{"status":"completed","content":[{"text":"Weather in Mexico City, MX: 20.5°C (69.0°F), broken clouds. Humidity: 26%","annotations":[],"type":"output_text"}],"type":"message","role":"assistant"}],"object":"response"}
```

**Key Takeaways:**

1. **Use Official SDKs**: While custom implementations can work locally, Azure preview services may require specific SDK patterns
2. **Debug Request Structure**: When data extraction fails, log the entire object structure to understand the wrapper layers
3. **Environment Variables**: Always verify `.env` loading with `load_dotenv()` - don't assume it's automatic
4. **Local First**: Thorough local testing reveals integration issues before expensive Azure deployments
5. **Documentation Patterns**: Follow official Microsoft code samples for hosted agents, don't reinvent the protocol layer

**Next: Azure Deployment with Official Pattern**
- Build hosted_agent_v2 container
- Deploy as WeatherAgent6 to test official SDK in Azure environment
- Expectation: Should transition from "Starting" to "Running" status successfully

---

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
