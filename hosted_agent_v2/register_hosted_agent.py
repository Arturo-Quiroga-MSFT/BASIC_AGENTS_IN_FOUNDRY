"""Register a hosted agent version in Azure AI Foundry.

This script registers the FoundryCBAgent-based implementation (v5+).

Requires:
  AZURE_AI_PROJECT_ENDPOINT (new project endpoint in North Central US)
  ACR_IMAGE (full ACR image URL, e.g., aqr2d2acr001.azurecr.io/weatheragent:v5)
  AGENT_NAME (default: WeatherAgent6)
  OPENWEATHER_API_KEY (optional, for container env)
  
Note: Port 8088 is the FoundryCBAgent default (not 8080).
"""

import os
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import ImageBasedHostedAgentDefinition, ProtocolVersionRecord, AgentProtocol


def main() -> None:
    endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]
    image = os.environ.get("ACR_IMAGE", "aqr2d2acr001.azurecr.io/weatheragent:v5")
    agent_name = os.environ.get("AGENT_NAME", "WeatherAgent6")
    openweather = os.environ.get("OPENWEATHER_API_KEY", "")
    port = os.environ.get("PORT") or os.environ.get("DEFAULT_AD_PORT") or "8088"

    if not image:
        raise ValueError("ACR_IMAGE is required (e.g., aqr2d2acr001.azurecr.io/weatheragent:v5)")

    env_vars = {
        "AZURE_AI_PROJECT_ENDPOINT": endpoint,
        # Many hosting platforms probe the port in PORT (often 8080). FoundryCBAgent
        # defaults to DEFAULT_AD_PORT. We set both and let the container decide.
        "PORT": str(port),
        "DEFAULT_AD_PORT": str(port),
        "LOG_LEVEL": "INFO",
        "AGENT_NAME": agent_name,
        "AGENT_VERSION": "5",
    }

    if openweather:
        env_vars["OPENWEATHER_API_KEY"] = openweather

    definition = ImageBasedHostedAgentDefinition(
        container_protocol_versions=[
            ProtocolVersionRecord(protocol=AgentProtocol.RESPONSES, version="v1")
        ],
        cpu="1",
        memory="2Gi",
        image=image,
        environment_variables=env_vars,
    )

    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as client,
    ):
        agent = client.agents.create_version(
            agent_name=agent_name,
            description="Weather agent (hosted)",
            definition=definition,
        )

    print("Hosted agent version created:")
    print(f"  Name: {agent.name}")
    print(f"  Version: {agent.version}")


if __name__ == "__main__":
    main()
