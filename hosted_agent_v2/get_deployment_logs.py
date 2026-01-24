"""Get deployment logs for WeatherAgent6 to see what's failing."""

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

def main():
    endpoint = "https://r2d2-hosted-agents-project-resou.services.ai.azure.com/api/projects/r2d2-hosted-agents-project"
    
    credential = DefaultAzureCredential()
    client = AIProjectClient(endpoint=endpoint, credential=credential)
    
    agent_name = "WeatherAgent6"
    
    print(f"📋 Getting details for {agent_name}...")
    
    try:
        agent = client.agents.get(agent_name=agent_name)
        print(f"\n✅ Agent: {agent.name}")
        print(f"   ID: {agent.id}")
        
        # Try to get deployment/container information
        if hasattr(agent, 'definition'):
            print(f"\n📦 Definition:")
            definition = agent.definition
            print(f"   Kind: {definition.get('kind')}")
            print(f"   Image: {definition.get('image')}")
            print(f"   CPU: {definition.get('cpu')}")
            print(f"   Memory: {definition.get('memory')}")
            
            if 'container_protocol_versions' in definition:
                print(f"   Protocols: {definition['container_protocol_versions']}")
        
        # Check if there's any deployment status or error info
        if hasattr(agent, 'versions'):
            versions = agent.versions
            print(f"\n📌 Versions: {versions}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
