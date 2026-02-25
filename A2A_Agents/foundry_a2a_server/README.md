# Phase 2: Expose Foundry Agent as A2A Server

Use the Microsoft Agent Framework to expose an agent as an A2A-compliant endpoint that can be discovered and called by any A2A client (including Copilot Studio).

## Overview

This takes a Foundry-backed agent and wraps it with an A2A HTTP server using:
- **Python:** `agent-framework-a2a` package
- **C#:** `Microsoft.Agents.AI.Hosting.A2A.AspNetCore` NuGet package

The exposed agent will:
- Serve an Agent Card at `/.well-known/agent.json`
- Accept A2A messages at the configured endpoint
- Be discoverable and connectable from Copilot Studio's A2A connector

## Prerequisites

- Python 3.11+ or .NET 8
- A deployed Foundry agent (or Azure OpenAI model)
- A publicly accessible endpoint (for Copilot Studio to reach)

## Python Setup

```bash
pip install agent-framework-a2a --pre azure-identity
```

## C# Setup

```bash
dotnet add package Microsoft.Agents.AI.Hosting.A2A.AspNetCore --prerelease
dotnet add package Azure.AI.OpenAI --prerelease
dotnet add package Azure.Identity
dotnet add package Microsoft.Extensions.AI
```

## Key Concept

Once exposed as an A2A server, Copilot Studio can connect to it:
1. Go to Agents → Add an agent → Agent2Agent
2. Enter the A2A endpoint URL
3. Copilot Studio auto-discovers the agent card
4. Done

## Status

- [ ] Python A2A server prototype
- [ ] C# A2A server prototype
- [ ] Deploy to Azure (App Service or Container Apps)
- [ ] Connect from Copilot Studio

## References

- https://learn.microsoft.com/agent-framework/integrations/a2a
- https://learn.microsoft.com/microsoft-copilot-studio/add-agent-agent-to-agent
