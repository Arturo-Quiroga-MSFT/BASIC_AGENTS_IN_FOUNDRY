# Phase 1: Foundry Agent with A2A Tool

A Foundry agent that calls an external A2A-compliant agent as a tool.

## Overview

This demonstrates the `A2ATool` in the Foundry Agent Service — the simplest way to enable agent-to-agent communication. The Foundry agent maintains control and summarizes responses from the external agent.

## Prerequisites

- Azure subscription with an active Foundry project
- Model deployment (e.g., gpt-4o) in the project
- An external A2A-compliant agent endpoint to connect to
- Python 3.11+

## Setup

```bash
pip install azure-ai-projects[agents] azure-identity python-dotenv
```

## Environment Variables

```
FOUNDRY_PROJECT_ENDPOINT=https://<your-project>.services.ai.azure.com/api
FOUNDRY_MODEL_DEPLOYMENT_NAME=gpt-4o
A2A_PROJECT_CONNECTION_NAME=<your-a2a-connection-name>
```

## Steps

1. Create an A2A Connection in the Foundry portal:
   - Tools → Connect tool → Custom tab → Agent2Agent (A2A) → Create
   - Enter name, A2A endpoint URL, and authentication method

2. Run `verify_connection.py` to ensure credentials and connection work

3. Run `a2a_agent.py` to create an agent with the A2A tool and test it

## References

- https://learn.microsoft.com/azure/ai-foundry/agents/how-to/tools/agent-to-agent
- https://learn.microsoft.com/azure/ai-foundry/agents/concepts/agent-to-agent-authentication
