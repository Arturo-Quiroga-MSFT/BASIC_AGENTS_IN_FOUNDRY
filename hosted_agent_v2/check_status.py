"""Check status of a hosted agent in Azure AI Foundry."""

import os
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

def main():
    endpoint = os.environ.get(
        "AZURE_AI_PROJECT_ENDPOINT",
        "https://r2d2-hosted-agents-project-resou.services.ai.azure.com/api/projects/r2d2-hosted-agents-project",
    )
    agent_name = os.environ.get("AGENT_NAME", "WeatherAgent6")
    
    credential = DefaultAzureCredential()
    client = AIProjectClient(endpoint=endpoint, credential=credential)
    
    print(f"Checking status for {agent_name}...")
    
    # Get the agent details
    agent = client.agents.get(agent_name=agent_name)
    
    print(f"\n✅ Agent Details:")
    print(f"   Name: {agent.name}")
    print(f"   ID: {agent.id}")
    
    # Print all available attributes
    print(f"\n   Available attributes:")
    for attr in dir(agent):
        if not attr.startswith('_'):
            try:
                val = getattr(agent, attr)
                if not callable(val):
                    print(f"      {attr}: {val}")
            except:
                pass

if __name__ == "__main__":
    main()
