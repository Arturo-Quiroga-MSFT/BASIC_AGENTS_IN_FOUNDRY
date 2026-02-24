"""Start deployment for a hosted agent in Azure AI Foundry."""

import os
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

def main():
    endpoint = "https://r2d2-hosted-agents-project-resou.services.ai.azure.com/api/projects/r2d2-hosted-agents-project"
    agent_name = "WeatherAgent6"
    
    credential = DefaultAzureCredential()
    client = AIProjectClient(endpoint=endpoint, credential=credential)
    
    print(f"Starting deployment for {agent_name}...")
    
    # Start the agent
    result = client.agents.start(agent_name=agent_name)
    
    print(f"✅ Deployment started!")
    print(f"   Agent: {result.name}")
    print(f"   Status: {result.status}")
    print(f"   Version: {result.version}")
    
    print("\nMonitor status with:")
    print(f"   python check_status.py")

if __name__ == "__main__":
    main()
