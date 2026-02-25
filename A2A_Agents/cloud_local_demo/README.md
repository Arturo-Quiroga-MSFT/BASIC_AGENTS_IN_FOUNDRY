# Cloud ↔ Local A2A Demo

**An on-device agent (Foundry Local) exposed as an A2A server, called by a cloud client (MAF A2AAgent) — all in Python.**

## What this demonstrates

| Concept | How it's shown |
|---|---|
| **A2A Protocol** | Standard agent-to-agent communication over HTTP |
| **Agent Discovery** | Client resolves the server's AgentCard at `/v1/card` |
| **Cloud ↔ Edge** | Cloud orchestrator delegates to an on-device agent |
| **Privacy** | Local agent processes everything on-device — nothing leaves the laptop |
| **Interop** | Server uses `a2a-sdk`, client uses MAF `agent-framework-a2a` — different libs, same protocol |

## Architecture

```
┌───────────────────────────────┐        A2A Protocol        ┌───────────────────────────────┐
│   CLOUD / CLIENT              │   ◄────────────────────►   │   LOCAL / SERVER               │
│                               │                            │                               │
│   cloud_a2a_client.py         │                            │   local_a2a_server.py          │
│   ┌─────────────────────┐     │                            │   ┌─────────────────────────┐  │
│   │ MAF A2AAgent        │     │                            │   │ a2a-sdk                 │  │
│   │ agent-framework-a2a │─────┼── GET /v1/card ───────────►│   │ A2AStarletteApplication │  │
│   │                     │─────┼── POST /v1/message:stream ►│   │                         │  │
│   └─────────────────────┘     │                            │   └────────────┬────────────┘  │
│                               │                            │                │               │
│   Resolves AgentCard,         │                            │   ┌────────────▼────────────┐  │
│   sends messages,             │                            │   │ Foundry Local           │  │
│   receives responses          │                            │   │ (Phi-4-mini / Qwen)     │  │
│                               │                            │   │ OpenAI-compatible API   │  │
│                               │                            │   │ localhost:5272          │  │
└───────────────────────────────┘                            │   └─────────────────────────┘  │
                                                             └───────────────────────────────┘
```

## Files

| File | Purpose |
|---|---|
| `local_a2a_server.py` | A2A server powered by Foundry Local — the "local/edge agent" |
| `cloud_a2a_client.py` | MAF A2A client — the "cloud orchestrator" connecting to the server |
| `requirements.txt` | Python dependencies for both server and client |
| `run_demo.sh` | Shell script to run the demo with one command |

## Prerequisites

### 1. Python environment

```bash
cd A2A_Agents/cloud_local_demo
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 2. Foundry Local

Install the Foundry Local CLI for your platform:

```bash
# macOS (when available via Homebrew)
brew install foundry-local

# Windows
winget install Microsoft.FoundryLocal

# Or download from:
# https://learn.microsoft.com/ai/foundry-local/get-started
```

Then pull a model:

```bash
foundry model run phi-4-mini      # ~2.4 GB, good balance
# or
foundry model run qwen2.5-0.5b    # ~350 MB, very fast
```

> **Note:** If `foundry-local-sdk` is not installed, the server falls back to connecting to `http://localhost:5272`. Just make sure Foundry Local is running somewhere:
> ```bash
> foundry service start
> foundry model run phi-4-mini
> ```

### 3. (Optional) For the `foundry-local-sdk` auto-start feature

```bash
pip install foundry-local-sdk
```

This lets the server auto-start the Foundry Local runtime and load the model automatically.

## Quick Start

### Option A: One-command demo

```bash
./run_demo.sh
```

This starts the A2A server in the background, waits for it to be ready, then launches an interactive chat client.

### Option B: Two terminals (recommended for learning)

**Terminal 1 — Start the A2A server:**

```bash
python local_a2a_server.py --model phi-4-mini --port 9999
```

You should see:
```
INFO: Starting Foundry Local with model 'phi-4-mini'...
INFO: Foundry Local ready at http://localhost:5272
INFO: Starting A2A server on port 9999...
INFO:   Agent Card:  http://localhost:9999/v1/card
INFO:   Messages:    POST http://localhost:9999/v1/message:stream
```

**Terminal 2 — Run the client:**

```bash
python cloud_a2a_client.py --host http://localhost:9999
```

You should see the AgentCard discovery, then an interactive prompt:
```
============================================================
  Agent Discovered via A2A
============================================================
  Name:        Foundry Local Agent
  Description: An on-device AI agent powered by Foundry Local (phi-4-mini)...
  Version:     0.1.0
  Skills:
    - Local On-Device Assistant: A privacy-focused assistant...
============================================================

Type your messages below. Type 'quit' or 'exit' to stop.

You: Hello! What can you do?
Agent: I'm a helpful assistant running on your local device...
```

### Option C: Single query (for scripting/testing)

```bash
python cloud_a2a_client.py --query "Explain the A2A protocol in 3 sentences"
```

### Smoke test

```bash
./run_demo.sh test
```

## How it works — step by step

1. **`local_a2a_server.py` starts:**
   - Connects to Foundry Local (starts it if `foundry-local-sdk` is installed)
   - Registers an `AgentCard` describing the agent's capabilities
   - Serves the A2A protocol on `http://localhost:9999/`

2. **`cloud_a2a_client.py` connects:**
   - Uses `A2ACardResolver` (from `a2a-sdk`) to fetch `http://localhost:9999/v1/card`
   - Wraps the endpoint with MAF's `A2AAgent`
   - Sends user messages via `agent.run(message)` — the A2A protocol handles the rest

3. **Message flow:**
   ```
   User types "Hello" →
     A2AAgent serializes as A2A message →
       POST to local server →
         AgentExecutor extracts text →
           Foundry Local chat completion →
             Response as A2A message →
               A2AAgent deserializes →
                 Printed to console
   ```

## Connecting from the real cloud

For a real Cloud ↔ Local demo (cloud agent on Azure calling your laptop):

### Using ngrok

```bash
# Terminal 3
ngrok http 9999
# Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
```

Then:

```bash
# Use the tunnel URL as the host
python cloud_a2a_client.py --host https://abc123.ngrok.io

# Or from Foundry Agent Service, create an A2A connection pointing to this URL
# Or from Copilot Studio, add an A2A agent with this URL
```

### Using VS Code Dev Tunnels

```bash
# In VS Code: Ctrl+Shift+P → "Forward a Port" → 9999
# Copy the generated URL
```

## Key Python packages

| Package | Role | Install |
|---|---|---|
| `a2a-sdk[http-server]` | A2A protocol server (Starlette) | `pip install "a2a-sdk[http-server]"` |
| `agent-framework-a2a` | MAF A2A client (A2AAgent) | `pip install agent-framework-a2a --pre` |
| `foundry-local-sdk` | Foundry Local runtime manager | `pip install foundry-local-sdk` |
| `openai` | Chat completions with Foundry Local | `pip install openai` |
| `uvicorn` | ASGI server | `pip install uvicorn` |
| `httpx` | HTTP client for card resolution | `pip install httpx` |

## Customization

**Change the model:**
```bash
python local_a2a_server.py --model qwen2.5-0.5b    # lighter, faster
python local_a2a_server.py --model phi-3.5-mini     # alternative
```

**Change the agent's personality:** Edit `SYSTEM_PROMPT` in `local_a2a_server.py`.

**Add tools:** Extend `FoundryLocalAgentExecutor.execute()` to call local tools before/after the LLM.

## Integration with the Multi-Agent Workshop

This demo fits into Ricardo's workshop as a lab exercise:

| Lab Step | Activity |
|---|---|
| Step 1 | Install Foundry Local + pull a model |
| Step 2 | Run `local_a2a_server.py` — explain A2A, AgentCard, skills |
| Step 3 | Run `cloud_a2a_client.py` — show discovery + message exchange |
| Step 4 | (Advanced) Set up ngrok → connect from Foundry Agent Service or Copilot Studio |
| Step 5 | Discussion: when to use A2A vs. MCP vs. direct API calls |

## References

| Topic | URL |
|---|---|
| A2A Protocol Spec | https://a2a-protocol.org/latest/ |
| a2a-sdk (Python) | https://github.com/a2aproject/a2a-python |
| MAF A2A Integration | https://learn.microsoft.com/agent-framework/integrations/a2a |
| MAF Python Samples | https://github.com/microsoft/agent-framework/tree/main/python/samples |
| Foundry Local Docs | https://learn.microsoft.com/ai/foundry-local/get-started |
| Foundry A2A Tool | https://learn.microsoft.com/azure/ai-foundry/agents/how-to/tools/agent-to-agent |
| Copilot Studio A2A | https://learn.microsoft.com/microsoft-copilot-studio/add-agent-agent-to-agent |
