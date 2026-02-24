# GitHub Issues to Post for Hosted Agents Problems

## Issue 1: azure-ai-foundry/foundry-samples

**URL**: https://github.com/azure-ai-foundry/foundry-samples/issues/new

**Title**: `[Hosted Agents] Container readiness probe fails - documentation doesn't specify health endpoint`

**Body**:
```markdown
## Description

When deploying a hosted agent following the official documentation, the deployment fails with `ContainerProbesFailed` error. The documentation doesn't clearly specify which health endpoint Azure Container Apps probes for readiness checks.

## Environment

- Region: North Central US
- SDK: azure-ai-projects==2.0.0b3
- Hosting Adapter: azure-ai-agentserver-agentframework==1.0.0b9
- Agent Framework: agent-framework==1.0.0b260107

## Steps to Reproduce

1. Create a hosted agent following the documentation at https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/hosted-agents
2. Use the sample Dockerfile pattern from the docs
3. Deploy using `client.agents.create_version()` and `az cognitiveservices agent start`
4. Deployment stays in "Starting" status indefinitely

## Error

Portal shows only one line in deployment logs:
```
[ContainerProbesFailed] User Error Occurred - Container readiness probes failed.
```

## Root Cause Found

The Dockerfile in documentation examples uses:
```dockerfile
HEALTHCHECK CMD curl -f http://localhost:8088/ || exit 1
```

But the hosting adapter exposes `/readiness` endpoint, not `/`. Azure Container Apps probes `/readiness`.

## Suggested Fix

1. Update documentation to clarify that the hosting adapter provides `/readiness` and `/health` endpoints
2. Update sample Dockerfiles to use:
```dockerfile
HEALTHCHECK CMD curl -f http://localhost:8088/readiness || exit 1
```
3. Document the expected health endpoints in the "Package code and test locally" section

## Additional Issue: Container Log API Not Working

The documented REST API for viewing container logs returns `UnsupportedAction`:

**Documented endpoint:**
```
GET /agents/v2.0/.../containers/default:logstream?kind=console&tail=50
```

**Response:**
```json
{"error":{"code":"UnsupportedAction","message":"The requested action 'agents/.../containers/default:logstream' is not supported"}}
```

This makes troubleshooting deployment failures very difficult as the only diagnostic information is the single-line error in the portal.

## Related Documentation

- https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/hosted-agents
- https://github.com/azure-ai-foundry/foundry-samples/tree/main/samples/python/hosted-agents
```

---

## Issue 2: Azure/azure-sdk-for-python

**URL**: https://github.com/Azure/azure-sdk-for-python/issues/new

**Title**: `[azure-ai-projects] Hosted agent deployment fails silently - no SDK method to retrieve container logs`

**Body**:
```markdown
## Description

When deploying hosted agents using `azure-ai-projects` SDK, there's no way to retrieve container logs to diagnose deployment failures. The REST API documented in Microsoft Learn for log streaming returns `UnsupportedAction`.

## Package Information

- **Package**: azure-ai-projects
- **Version**: 2.0.0b3
- **Related packages**: 
  - azure-ai-agentserver-agentframework==1.0.0b9
  - agent-framework==1.0.0b260107

## Environment

- Python: 3.12.12
- OS: macOS / deployed to North Central US

## Steps to Reproduce

1. Create and deploy a hosted agent:
```python
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import ImageBasedHostedAgentDefinition, ProtocolVersionRecord, AgentProtocol

client = AIProjectClient(endpoint=PROJECT_ENDPOINT, credential=DefaultAzureCredential())

agent = client.agents.create_version(
    agent_name="my-agent",
    definition=ImageBasedHostedAgentDefinition(
        container_protocol_versions=[ProtocolVersionRecord(protocol=AgentProtocol.RESPONSES, version="v1")],
        cpu="1",
        memory="2Gi",
        image="myregistry.azurecr.io/myagent:v1",
        environment_variables={...}
    )
)
```

2. Start the agent with CLI: `az cognitiveservices agent start ...`
3. Deployment fails or stays stuck in "Starting"
4. **No SDK method exists to retrieve logs**

## Expected Behavior

The SDK should provide a method like:
```python
logs = client.agents.get_deployment_logs(agent_name="my-agent", agent_version=1, kind="console", tail=100)
```

## Actual Behavior

- No SDK method for logs
- Documented REST API returns error:
```json
{"error":{"code":"UnsupportedAction","message":"The requested action 'agents/my-agent/versions/1/containers/default:logstream' is not supported"}}
```
- Portal shows only terse single-line error: `[ContainerProbesFailed] User Error Occurred`

## Impact

Without access to container logs, debugging hosted agent deployments is extremely difficult. Users have no visibility into:
- Container startup errors
- Python exceptions
- Missing dependencies
- Configuration issues

## Suggested Enhancement

Add methods to `AIProjectClient.agents`:
- `get_container_logs(agent_name, agent_version, kind="console", tail=100)`
- `get_deployment_status(agent_name, agent_version)` with detailed error information

## Related

- Documentation: https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/hosted-agents#view-container-log-stream
- The REST API section documents log streaming but it's not implemented
```

---

## Issue 3: Azure/azure-cli

**URL**: https://github.com/Azure/azure-cli/issues/new

**Title**: `[cognitiveservices agent] Add command to retrieve container logs for hosted agent troubleshooting`

**Body**:
```markdown
## Description

The `az cognitiveservices agent` command group (preview) lacks a command to retrieve container logs for hosted agent deployments. This makes troubleshooting failed deployments very difficult.

## CLI Version

```
az version: 2.x.x (latest)
Extension: cognitiveservices (preview)
```

## Current Commands Available

```bash
az cognitiveservices agent start
az cognitiveservices agent stop
az cognitiveservices agent show
az cognitiveservices agent list-versions
az cognitiveservices agent update
az cognitiveservices agent delete
az cognitiveservices agent delete-deployment
```

## Missing Command

There's no command to retrieve container logs:
```bash
az cognitiveservices agent logs  # Does not exist
```

## Steps to Reproduce the Need

1. Deploy a hosted agent:
```bash
az cognitiveservices agent start \
  --account-name "my-account" \
  --project-name "my-project" \
  --name "my-agent" \
  --agent-version 1
```

2. Deployment fails or stays stuck in "Starting" status
3. **No CLI command to see why**

## Expected Behavior

A command like:
```bash
az cognitiveservices agent logs \
  --account-name "my-account" \
  --project-name "my-project" \
  --name "my-agent" \
  --agent-version 1 \
  --kind console \
  --tail 100
```

Should output container stdout/stderr logs similar to:
```
2025-01-24T08:43:48.72656  Starting agent...
2025-01-24T08:43:49.12345  Error: Missing environment variable AZURE_OPENAI_ENDPOINT
```

## Actual Behavior

- No logs command exists
- The documented REST API for log streaming returns `UnsupportedAction`
- Portal shows only: `[ContainerProbesFailed] User Error Occurred`

## Impact

Users deploying hosted agents have no CLI-based way to troubleshoot failures. The only option is to check the Azure Portal, which shows minimal information.

## Documentation Reference

The REST API for logs is documented here but doesn't work:
https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/hosted-agents#view-container-log-stream

## Suggested Implementation

Add `az cognitiveservices agent logs` command with parameters:
- `--account-name` (required)
- `--project-name` (required)  
- `--name` (required)
- `--agent-version` (required)
- `--kind` (optional: console/system, default: console)
- `--tail` (optional: 1-300, default: 20)
- `--follow` (optional: stream logs in real-time)
```

---

## Quick Links to Create Issues

1. **Foundry Samples**: https://github.com/azure-ai-foundry/foundry-samples/issues/new
2. **Azure SDK for Python**: https://github.com/Azure/azure-sdk-for-python/issues/new  
3. **Azure CLI**: https://github.com/Azure/azure-cli/issues/new

Copy the title and body for each issue from above.
