# Hosted Agent V3 - Foundry SDK Implementation

This directory contains a hosted agent implementation following the official Microsoft documentation:
https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/hosted-agents?view=foundry&tabs=foundry-sdk

## Overview

This implementation uses:
- **Azure AI Projects SDK** for hosted agent creation and management
- **Hosting adapter** for local testing and deployment
- **Azure Container Registry** for image hosting
- **Foundry Agent Service** for managed hosting

## Directory Structure

```
hosted_agents_v3/
├── agent.py              # Main agent code with hosting adapter
├── requirements.txt      # Python dependencies
├── Dockerfile           # Container image definition
├── test_local.py        # Local testing script
├── create_agent.py      # Script to create hosted agent using SDK
├── manage_agent.py      # Script to manage agent lifecycle
├── invoke_agent.py      # Script to test deployed agent
├── .env.example         # Environment variables template
└── README.md           # This file
```

## Prerequisites

- Microsoft Foundry project
- Azure Container Registry
- Azure CLI installed
- Docker installed
- Python 3.8+

## Setup Steps

1. Install dependencies: `pip install -r requirements.txt`
2. Configure environment variables (copy `.env.example` to `.env`)
3. Run agent locally: `python agent.py`
4. Test locally: `python test_local.py`
5. Build Docker image: `docker build -t myagent:v1 .`
6. Push to ACR (see deployment guide)
7. Create hosted agent: `python create_agent.py`
8. Start deployment: Use Azure CLI or management script
9. Invoke agent: `python invoke_agent.py`

## Status

- [x] Prerequisites installed
- [ ] Agent code created
- [ ] Local testing completed
- [ ] Docker image created
- [ ] ACR push completed
- [ ] Capability host created
- [ ] Hosted agent created
- [ ] Agent deployed
- [ ] Agent tested

## References

- [Official Documentation](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/hosted-agents?view=foundry&tabs=foundry-sdk)
- [Python Samples](https://github.com/azure-ai-foundry/foundry-samples/tree/main/samples/python/hosted-agents)
