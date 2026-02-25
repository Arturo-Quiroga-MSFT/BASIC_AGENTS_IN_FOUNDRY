# Phase 3: Non-Microsoft Agent as A2A Server

Build an agent using a non-Microsoft framework (Google ADK, LangGraph, raw OpenAI, etc.) and expose it as an A2A-compliant server that Copilot Studio can orchestrate.

## Overview

This is the **cross-platform interop** scenario — the real power of A2A. The goal:

1. Build an agent with a non-MSFT framework
2. Expose it as an A2A server (HTTP + Agent Card)
3. Connect it to Copilot Studio via the A2A connector
4. Let the Copilot Studio orchestrator decide when to call it

## Candidate Frameworks

| Framework | Language | A2A Support | Notes |
|---|---|---|---|
| **Google ADK** | Python | Native | Google originated the A2A protocol; ADK has built-in A2A server support |
| **LangGraph** | Python | Via adapter | Community A2A adapters exist |
| **CrewAI** | Python | Via adapter | Community A2A support |
| **Raw OpenAI** | Python/JS | Manual | Build A2A server around `openai` SDK calls |
| **AutoGen** | Python | Via adapter | Microsoft framework but non-Foundry |

## Simplest Path: Google ADK

Google ADK has first-class A2A support since Google created the protocol:

```python
# Conceptual — exact API may vary
from google.adk.agents import Agent
from google.adk.a2a import A2AServer

agent = Agent(name="google_weather", model="gemini-2.0-flash-001")
server = A2AServer(agent, port=8080)
server.run()  # Exposes /.well-known/agent.json + A2A endpoints
```

## Simplest Path: Raw OpenAI + A2A Library

```python
# Using the a2a-python reference library
from a2a.server import A2AServer
from openai import OpenAI

client = OpenAI()

async def handle_message(message):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": message.text}]
    )
    return response.choices[0].message.content

server = A2AServer(handler=handle_message, port=8080)
server.run()
```

## Integration with Copilot Studio

Once the non-MSFT A2A server is deployed and publicly accessible:

1. In Copilot Studio: Agents → Add an agent → **Agent2Agent**
2. Enter the endpoint URL (e.g., `https://my-google-agent.azurewebsites.net/a2a`)
3. Copilot Studio auto-discovers the agent card from `.well-known/agent.json`
4. Select auth (if any)
5. The non-MSFT agent is now part of the Copilot Studio orchestration mesh

## Status

- [ ] Choose framework (Google ADK recommended for demo clarity)
- [ ] Build simple agent
- [ ] Expose as A2A server
- [ ] Deploy publicly
- [ ] Connect from Copilot Studio
- [ ] Document for workshop

## References

- https://a2a-protocol.org/latest/
- https://google.github.io/adk-docs/
- https://github.com/a2aproject/a2a-python (reference implementation)
- https://learn.microsoft.com/microsoft-copilot-studio/add-agent-agent-to-agent
