"""Stop and delete old non-working hosted agents."""

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
import time

def main():
    endpoint = "https://r2d2-hosted-agents-project-resou.services.ai.azure.com/api/projects/r2d2-hosted-agents-project"
    
    # Agents to delete (the failed ones)
    agents_to_cleanup = [
        "WeatherAgent",
        "WeatherAgent2",
        "WeatherAgent3",
        "WeatherAgent4",
        "WeatherAgent5"
    ]
    
    credential = DefaultAzureCredential()
    client = AIProjectClient(endpoint=endpoint, credential=credential)
    
    print("🛑 Stopping old failed hosted agents...")
    
    for agent_name in agents_to_cleanup:
        try:
            print(f"   Stopping {agent_name}...", end=" ")
            # Try to stop using REST API since SDK doesn't have stop method
            # We'll just try to delete directly and let it fail gracefully
            client.agents.delete(agent_name=agent_name)
            print("✅")
        except Exception as e:
            error_msg = str(e)
            if "active associated hosted containers" in error_msg:
                print(f"⚠️  Has active containers (needs manual stop in portal)")
            else:
                print(f"⚠️  {e}")
    
    print("\n💡 To delete these agents:")
    print("   1. Go to Azure portal or Foundry UI")
    print("   2. Stop each agent manually")
    print("   3. Then run this script again to delete")
    print("\nAlternatively, they can stay stopped - they won't cost anything.")

if __name__ == "__main__":
    main()
