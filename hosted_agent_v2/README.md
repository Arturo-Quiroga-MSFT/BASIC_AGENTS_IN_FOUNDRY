# WeatherAgent v2 - Official Azure AI Agent Server Implementation

This implementation uses the official `azure-ai-agentserver-core` package following Microsoft's recommended pattern for hosted agents.

## Overview

After multiple failed attempts with a custom aiohttp server implementation (which worked locally but failed to start in Azure), we migrated to the official Microsoft SDK pattern. This version successfully runs locally and is ready for Azure deployment.

## Key Components

### agent.py
Main agent implementation using `FoundryCBAgent` class:
- **Request Handler**: `agent_run(request_body)` processes incoming requests
- **Weather Function**: `get_weather(location)` queries OpenWeatherMap API
- **Response Builder**: Creates OpenAI-compatible response objects
- **Streaming Support**: Optional streaming with delta events

### Architecture

```python
from azure.ai.agentserver.core import FoundryCBAgent

async def agent_run(request_body):
    # request_body is AgentRunContext wrapper
    # Access actual request: request_body.request (dict)
    # Extract messages: request_body.request['messages']
    # Process query and return OpenAIResponse
    pass

my_agent = FoundryCBAgent()
my_agent.agent_run = agent_run
my_agent.run()  # Starts on port 8088
```

## Request Flow

1. **Incoming Request**: POST to `/responses` endpoint
   ```json
   {
     "messages": [{"role": "user", "content": "What is the weather in Mexico City?"}],
     "model": "weather-agent",
     "stream": false
   }
   ```

2. **SDK Processing**: FoundryCBAgent wraps request in `AgentRunContext`
   - `request_body.request` → Original request dict
   - `request_body.stream` → Streaming flag
   - `request_body.response_id` → Unique response ID

3. **Message Extraction**:
   ```python
   if hasattr(request_body, 'request') and isinstance(request_body.request, dict):
       messages = request_body.request.get('messages', [])
       for msg in messages:
           if isinstance(msg, dict) and msg.get('role') == 'user':
               user_message = msg.get('content', '')
   ```

4. **Query Processing**: Pattern match for weather queries
   ```python
   match = re.search(r'weather (?:in|for) ([A-Za-z\s]+)', user_message, re.IGNORECASE)
   if match:
       city = match.group(1).strip()
       response_text = await get_weather(city)
   ```

5. **Response Building**: Return OpenAIResponse object
   ```python
   output_content = [ItemContentOutputText(text=response_text, annotations=[])]
   response = OpenAIResponse(
       metadata={},
       id=f"resp_{datetime.datetime.now().timestamp()}",
       created_at=datetime.datetime.now(),
       output=[ResponsesAssistantMessageItemResource(
           status="completed",
           content=output_content
       )]
   )
   ```

## Environment Setup

### Required Environment Variables (.env)

```bash
# OpenWeather API Key (REQUIRED - must load with dotenv)
OPENWEATHER_API_KEY=your_api_key_here

# Azure Configuration (optional for local testing)
AZURE_AI_PROJECT_ENDPOINT=https://your-project.services.ai.azure.com/
AZURE_CLIENT_ID=your_client_id
AZURE_CLIENT_SECRET=your_client_secret
AZURE_TENANT_ID=your_tenant_id

# Agent Configuration
PORT=8088  # FoundryCBAgent default
LOG_LEVEL=INFO
AGENT_NAME=WeatherAgent
AGENT_VERSION=5
```

### Critical: Environment Loading

**Must** call `load_dotenv()` before other imports:

```python
import os
from dotenv import load_dotenv

# Load .env file FIRST
load_dotenv()

from azure.ai.agentserver.core import FoundryCBAgent
# ... rest of imports
```

Without this, `os.getenv("OPENWEATHER_API_KEY")` returns `None` even if `.env` exists.

## Local Testing

### 1. Install Dependencies

```bash
# Use project virtual environment
cd /path/to/BASIC_AGENTS_IN_FOUNDRY
source .venv/bin/activate

# Install requirements
cd hosted_agent_v2
pip install -r requirements.txt
```

Dependencies:
- `azure-ai-agentserver-core==1.0.0b8` - Official agent server
- `httpx==0.26.0` - HTTP client for weather API
- `python-dotenv==1.0.0` - Environment variable loading

### 2. Configure Environment

```bash
# Copy example and edit
cp .env.example .env
nano .env  # Add your OPENWEATHER_API_KEY
```

### 3. Run Agent

```bash
python agent.py
```

Expected output:
```
environment variable APPLICATIONINSIGHTS_CONNECTION_STRING not set.
environment variable AGENT_PROJECT_RESOURCE_ID not set.
INFO:azure.identity.aio._credentials.environment:No environment configuration found.
INFO:azure.identity.aio._credentials.managed_identity:ManagedIdentityCredential will use IMDS
2026-01-23 18:32:12,212 - azure.ai.agentserver - INFO - Starting FoundryCBAgent server on port 8088
INFO:     Started server process [23213]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8088 (Press CTRL+C to quit)
```

Note: Environment variable warnings are normal for local testing.

### 4. Test with curl

```bash
# Weather query
curl -X POST http://localhost:8088/responses \
  -H "Content-Type: application/json" \
  -d '{
    "messages":[{"role":"user","content":"What is the weather in Mexico City?"}],
    "model":"weather-agent",
    "stream":false
  }'
```

Success response:
```json
{
  "metadata": {},
  "temperature": 0.0,
  "top_p": 0.0,
  "user": "user",
  "id": "resp_1769211657.422282",
  "created_at": 1769193657,
  "output": [{
    "status": "completed",
    "content": [{
      "text": "Weather in Mexico City, MX: 20.5°C (69.0°F), broken clouds. Humidity: 26%",
      "annotations": [],
      "type": "output_text"
    }],
    "type": "message",
    "role": "assistant"
  }],
  "object": "response"
}
```

## Docker Build

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy agent code
COPY agent.py .

# Expose port 8088 (FoundryCBAgent default)
EXPOSE 8088

# Run agent
CMD ["python", "agent.py"]
```

### Build and Test Container

```bash
# Build image
docker build -t weatheragent:v5 .

# Run container (with .env for local testing)
docker run -d \
  --name weatheragent-v5 \
  -p 8088:8088 \
  --env-file .env \
  weatheragent:v5

# Check logs
docker logs weatheragent-v5

# Test
curl -X POST http://localhost:8088/responses \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"What is the weather in Tokyo?"}],"model":"weather-agent","stream":false}'

# Cleanup
docker stop weatheragent-v5
docker rm weatheragent-v5
```

## Azure Deployment

### Prerequisites

- Azure Container Registry: `aqr2d2acr001.azurecr.io`
- Azure AI Foundry Project: `r2d2-hosted-agents-project` (North Central US)
- Subscription: `7a28b21e-0d3e-4435-a686-d92889d4ee96`
- Capability Host: `accountcaphost` (with `enablePublicHostingEnvironment: true`)

### ACR Permissions

Ensure both managed identities have AcrPull role:

```bash
# Account managed identity
az role assignment create \
  --assignee e4c57853-4452-4012-af86-97f7527b1e10 \
  --role AcrPull \
  --scope /subscriptions/7a28b21e-0d3e-4435-a686-d92889d4ee96/resourceGroups/AQ-FOUNDRY-RG/providers/Microsoft.ContainerRegistry/registries/aqr2d2acr001

# Project managed identity
az role assignment create \
  --assignee a0d1a4e7-3ebc-4556-8a9b-d04d6c5e0239 \
  --role AcrPull \
  --scope /subscriptions/7a28b21e-0d3e-4435-a686-d92889d4ee96/resourceGroups/AQ-FOUNDRY-RG/providers/Microsoft.ContainerRegistry/registries/aqr2d2acr001
```

### Push to ACR

```bash
# Login to ACR
az acr login --name aqr2d2acr001

# Tag image
docker tag weatheragent:v5 aqr2d2acr001.azurecr.io/weatheragent:v5

# Push to registry
docker push aqr2d2acr001.azurecr.io/weatheragent:v5
```

### Register Hosted Agent

Use the SDK script (adapt from `../hosted_agent/register_hosted_agent.py`):

```python
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    ImageBasedHostedAgentDefinition,
    AgentProtocol
)
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
project_client = AIProjectClient.from_connection_string(
    credential=credential,
    conn_str="ENDPOINT;SUBSCRIPTION_ID;RESOURCE_GROUP;PROJECT_NAME"
)

definition = ImageBasedHostedAgentDefinition(
    image="aqr2d2acr001.azurecr.io/weatheragent:v5",
    port=8088,
    protocol=AgentProtocol.RESPONSES
)

agent = project_client.agents.create_hosted_agent(
    name="WeatherAgent6",
    hosted_agent_definition=definition
)

print(f"Created hosted agent: {agent.name} (ID: {agent.id})")
```

### Start Deployment

```bash
# Using Azure CLI
az ai agent start \
  --project-name "r2d2-hosted-agents-project" \
  --agent-name "WeatherAgent6"

# Monitor status
az ai agent show \
  --project-name "r2d2-hosted-agents-project" \
  --agent-name "WeatherAgent6" \
  --query "status"
```

Expected: Should transition from "Starting" to "Running" (unlike custom implementation which got stuck).

## Differences from Custom Implementation

| Aspect | Custom (hosted_agent) | Official (hosted_agent_v2) |
|--------|----------------------|---------------------------|
| **Server** | aiohttp + manual routing | FoundryCBAgent (uvicorn) |
| **Port** | 8080 | 8088 |
| **Request Object** | Raw HTTP body dict | AgentRunContext wrapper |
| **Message Access** | Direct from body | `request_body.request['messages']` |
| **Protocol Handling** | Manual Activity + Responses | Automatic SDK translation |
| **Tracing** | Manual logging | Built-in OpenTelemetry |
| **Local Testing** | ✅ Success | ✅ Success |
| **Azure Deployment** | ❌ Stuck in "Starting" | ⏳ To be tested |

## Troubleshooting

### "Error: Weather API key not configured"

**Cause**: `.env` file not loaded or OPENWEATHER_API_KEY not set

**Solution**:
1. Verify `.env` file exists with key: `OPENWEATHER_API_KEY=...`
2. Ensure `load_dotenv()` called at module level in `agent.py`
3. Restart agent after changing `.env`

### Empty user_message extracted

**Cause**: Incorrect request structure access

**Solution**: Use the correct path:
```python
# ✅ Correct
messages = request_body.request.get('messages', [])

# ❌ Wrong
messages = request_body.messages  # Doesn't exist
```

### Port 8088 already in use

**Cause**: Previous agent instance still running

**Solution**:
```bash
# Find and kill process
lsof -ti:8088 | xargs kill -9

# Or use docker
docker ps | grep weatheragent
docker stop <container_id>
```

## Next Steps

1. ✅ Local testing successful
2. ⏳ Build Docker container
3. ⏳ Push to Azure Container Registry
4. ⏳ Register as WeatherAgent6
5. ⏳ Deploy and verify "Running" status
6. ⏳ Test via Azure endpoint
7. ⏳ Integrate with Agent365

## Resources

- [Azure AI Agent Server Core Docs](https://learn.microsoft.com/azure/ai-foundry/agents/concepts/hosted-agents)
- [FoundryCBAgent Code Sample](https://learn.microsoft.com/azure/ai-foundry/agents/code-samples/hosted-agents-custom)
- [Responses Protocol Specification](https://learn.microsoft.com/azure/ai-foundry/agents/concepts/responses-protocol)
- [OpenWeatherMap API](https://openweathermap.org/api)
