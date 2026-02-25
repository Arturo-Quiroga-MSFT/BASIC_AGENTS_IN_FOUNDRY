# A2A Agents — Exploration & Prototypes

This folder contains exploration work for integrating agents via the **Agent2Agent (A2A) protocol**, in support of Ricardo Mejia's multi-agent workshop.

## Context

Ricardo's team built a [Multi-Agent Hands-On Lab](https://github.com/warnov/multi-agentic-workshop/tree/master/en) with Fabric + Foundry + Copilot Studio. They now want to extend it with:

1. **A2A protocol** for Foundry agent interop
2. **Non-Microsoft agents** (Google, OpenAI, LangGraph, etc.) connected via A2A to Copilot Studio

## Structure

```
A2A_Agents/
├── cloud_local_demo/       # ⭐ Cloud ↔ Local A2A demo (MAF + Foundry Local)
├── foundry_a2a_tool/       # Phase 1: Foundry agent calling external agents via A2A Tool
├── foundry_a2a_server/     # Phase 2: Expose Foundry agent as A2A endpoint
├── non_msft_a2a_agent/     # Phase 3: Non-MSFT agent (Google ADK / LangGraph / OpenAI) as A2A server
├── arturos_idea_for_demo/  # Architecture notes for the Cloud ↔ Local concept
```

## Key References

| Topic | URL |
|---|---|
| A2A Protocol Spec | https://a2a-protocol.org/latest/ |
| Foundry A2A Tool (Python) | https://learn.microsoft.com/azure/ai-foundry/agents/how-to/tools/agent-to-agent |
| Copilot Studio A2A Connector | https://learn.microsoft.com/microsoft-copilot-studio/add-agent-agent-to-agent |
| Microsoft Agent Framework A2A | https://learn.microsoft.com/agent-framework/integrations/a2a |
| Multi-Agent Patterns (Copilot Studio) | https://learn.microsoft.com/microsoft-copilot-studio/guidance/architecture/multi-agent-patterns |
| Agent Framework A2A Python pkg | `pip install agent-framework-a2a --pre` |
| Foundry SDK | `pip install azure-ai-projects[agents]` |

## Status

- [x] **Cloud ↔ Local A2A Demo** — `a2a-sdk` server (Foundry Local) + MAF `A2AAgent` client
- [ ] Phase 1 — Foundry agent with A2A Tool
- [ ] Phase 2 — Foundry agent exposed as A2A server
- [ ] Phase 3 — Non-MSFT agent as A2A server → Copilot Studio
- [ ] Phase 4 — Workshop lab integration
