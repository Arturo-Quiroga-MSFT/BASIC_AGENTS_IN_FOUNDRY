"""Delete old non-working hosted agents."""

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

def main():
    endpoint = "https://r2d2-hosted-agents-project-resou.services.ai.azure.com/api/projects/r2d2-hosted-agents-project"
    
    # Agents to delete (the failed ones)
    agents_to_delete = [
        "WeatherAgent",
        "WeatherAgent2",
        "WeatherAgent3",
        "WeatherAgent4",
        "WeatherAgent5"
    ]
    
    credential = DefaultAzureCredential()
    client = AIProjectClient(endpoint=endpoint, credential=credential)
    
    print("🗑️  Deleting old failed hosted agents...")
    
    for agent_name in agents_to_delete:
        try:
            print(f"   Deleting {agent_name}...", end=" ")
            client.agents.delete(agent_name=agent_name)
            print("✅")
        except Exception as e:
            print(f"⚠️  {e}")
    
    print("\n✅ Cleanup complete! WeatherAgent6 remains.")

if __name__ == "__main__":
    main()
