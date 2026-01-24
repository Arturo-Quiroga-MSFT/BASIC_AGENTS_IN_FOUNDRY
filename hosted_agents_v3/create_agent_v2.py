#!/usr/bin/env python3
"""
Create version 2 of the hosted agent with the fixed Docker image.
"""
import os
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import ImageBasedHostedAgentDefinition, ProtocolVersionRecord, AgentProtocol
from azure.identity import DefaultAzureCredential

load_dotenv()

# Configuration
PROJECT_ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
AGENT_NAME = os.getenv("AGENT_NAME", "my-hosted-agent")
CONTAINER_IMAGE = "aqr2d2acr001.azurecr.io/myhostedagent:v2"  # New v2 image

print(f"Creating agent version 2 with fixed image...")
print(f"Project endpoint: {PROJECT_ENDPOINT}")
print(f"Agent name: {AGENT_NAME}")
print(f"Container image: {CONTAINER_IMAGE}")

# Initialize the client
client = AIProjectClient(
    endpoint=PROJECT_ENDPOINT,
    credential=DefaultAzureCredential()
)

# Create the agent version 2 with the fixed image
agent = client.agents.create_version(
    agent_name=AGENT_NAME,
    definition=ImageBasedHostedAgentDefinition(
        container_protocol_versions=[
            ProtocolVersionRecord(protocol=AgentProtocol.RESPONSES, version="v1")
        ],
        cpu="1",
        memory="2Gi",
        image=CONTAINER_IMAGE,
        environment_variables={
            "AZURE_AI_PROJECT_ENDPOINT": PROJECT_ENDPOINT,
            "AZURE_OPENAI_ENDPOINT": os.getenv("AZURE_OPENAI_ENDPOINT"),
            "AZURE_OPENAI_CHAT_DEPLOYMENT_NAME": os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
        }
    )
)

print(f"\n✅ Agent version created successfully!")
print(f"   Agent Name: {agent.name}")
print(f"   Version: {agent.version}")
print(f"   ID: {agent.id}")

print(f"\n📝 Next steps:")
print(f"   1. Start the agent: az cognitiveservices agent start \\")
print(f"      --account-name 'r2d2-hosted-agents-project-resou' \\")
print(f"      --project-name 'r2d2-hosted-agents-project' \\")
print(f"      --name '{AGENT_NAME}' \\")
print(f"      --agent-version {agent.version}")
print(f"   2. Wait 2-5 minutes for deployment")
print(f"   3. Test with: python invoke_agent.py")
